import datetime
import time
from argparse import ArgumentParser
from threading import Thread
from _pysha3 import keccak_256 as sha3_256
from multiprocessing import Process
from flask import Flask, jsonify, request, abort, Response
from blockchain import Blockchain
from dctp import ServerDCTP, send_status_code
from fog_nodes_manager import ManagerFogNodes
from utils import exists_path, get_path, append_pool_host, LoadJsonFile, get_pools_host, SaveJsonFile
from variables import POOL_PORT, POOL_CM_PORT, POOL_FN_PORT
from wallet import Wallet
import requests
import json as _json
from random import choice


class Pool(Process):
    def __init__(self, private_key, port_pool=POOL_PORT, port_cm=POOL_CM_PORT, port_fn=POOL_FN_PORT):
        super().__init__()
        self._wallet = Wallet(private_key)
        SaveJsonFile('data/pool/key', private_key)
        self._port_cm = port_cm
        self._port_fn = port_fn
        self._port_pool = port_pool
        self._active_pools = {}
        self._blockchain_thread = None

    @property
    def _blockchain(self):
        while self._blockchain_thread is None or not self._blockchain_thread.is_alive():
            time.sleep(0.1)
        return self._blockchain_thread

    @staticmethod
    def get_my_ip():
        pools = get_pools_host('data/pool/pools_host')
        while True:
            try:
                ip, port, _, _ = pools[choice(list(pools))]
                return requests.get(f'http://{ip}:{port}/get_my_ip').json()
            except:
                time.sleep(1)
                pass

    def run(self):
        if not Wallet.check_valid_address(self._wallet.address):
            raise Exception(f'Pool address {self._wallet.address} is not valid')

        server_CM = ServerDCTP(self._port_cm)

        @server_CM.method('send_replica')
        def send_replica(json, data):
            with open(get_path(f'data/pool/waiting_replicas/{sha3_256(data).hexdigest()}'), 'wb') as f:
                f.write(data)

        @server_CM.method('commit_replica')
        def commit_replica(json, data):
            if not all([key in json for key in ['id_client', 'data']]):
                return send_status_code(100, 'Required parameters are not specified: id_client, data')

            code, text = self._blockchain.new_transaction(sender=json['id_client'], data=json['data'],
                                                          date=datetime.datetime.utcnow().timestamp(), is_cm=True)
            return send_status_code(code, text)

        @server_CM.method('new_transaction')
        def new_transaction(json, data):
            if not all([key in json for key in ['sender', 'owner', 'count']]):
                return send_status_code(100, 'Required parameters are not specified: sender, owner, count')

            json['sender'] = json['sender'].lstrip().rstrip()
            json['owner'] = json['owner'].lstrip().rstrip()
            if json['sender'] == json['owner']:
                return send_status_code(100, 'Are you stupid? why send byteEx yourself.')

            if type(json['count']) == int:
                if json['count'] <= 0:
                    return send_status_code(100, 'Required parameter "count" must be greater than zero')
            else:
                return send_status_code(100, 'Required parameter "count" must be a number')

            code, text = self._blockchain.new_transaction(sender=json['sender'], owner=json['owner'],
                                                          count=json['count'],
                                                          date=datetime.datetime.utcnow().timestamp(), is_cm=True)
            return send_status_code(code, text)

        @server_CM.method('get_occupied')
        def get_occupied(json, data):
            return {'occupied': self._blockchain.get_occupied(json['id_client'])}

        @server_CM.method('get_info_object')
        def get_info_object(json, data):
            return {'info': self._blockchain.get_info_object(json['id_client'], json['id_object'])}

        @server_CM.method('get_all_ns')
        def get_all_ns(json, data):
            return {'all_ns': self._blockchain._dns.get_all_ns(json['id_client'])}

        @server_CM.method('registration_domain_name')
        def registration_domain_name(json, data):
            if not all([key in json for key in ['address', 'name']]):
                return send_status_code(100, 'Required parameters are not specified: address, name')
            if type(json['name']) != str or not json['name'].strip():
                return send_status_code(100, 'Parameter "name" is not valid')

            replica = ['ns', json['name'], json['address']]
            hash_replica = sha3_256(bytes(_json.dumps(replica), 'utf-8')).hexdigest()
            SaveJsonFile(f'data/pool/waiting_replicas/{hash_replica}', replica)
            code, text = self._blockchain.new_transaction(sender=json['address'], data=hash_replica,
                                                          date=datetime.datetime.utcnow().timestamp(), is_cm=True)
            return send_status_code(code, text)

        @server_CM.method('check_valid_address')
        def check_valid_address(json, data):
            return {'address_normal': self._blockchain._dns.find_address(json['id_client'])}

        server_CM.start()

        server_FN = ServerDCTP(self._port_fn)

        @server_FN.method('connect_valid_client')
        def connect_valid_client(json):
            return Wallet.check_valid_address(json['id_worker'])

        @server_FN.method('on_connected')
        def on_connected(json):
            response = server_FN.request(id_worker=json['id_worker'], method='get_hash_replicas')
            if all([key in response for key in ['hash_replicas', 'size_fog_node']]):
                self._blockchain.add_fog_node(id_fog_node=json['id_worker'],
                                              data={'hash_replicas': response['hash_replicas'],
                                                    'size_fog_node': response['size_fog_node']})

        @server_FN.method('on_disconnected')
        def on_disconnected(json):
            self._blockchain.del_fog_node(json['id_worker'])

        @server_FN.method('get_balance')
        def get_balance(json, data):
            return {'amount': self._blockchain.get_balance(json['id_client'])}

        server_FN.start()

        # tun Flask - обмен данными между пулами
        flask_thread = Thread(target=self.run_flask, args=[server_FN])
        flask_thread.start()

        # получаем ip нашего пула
        self._ip_pool = self.get_my_ip()

        self._blockchain_thread = Blockchain(server_FN, self._wallet, self._ip_pool,
                                             self._port_pool, self._port_cm, self._port_fn)
        self._blockchain_thread.start()

        while True:
            if not (flask_thread.is_alive() and server_FN.is_alive()
                    and server_CM.is_alive() and self._blockchain_thread.is_alive()):
                print(f'Error POOL {self._wallet.address} flask={flask_thread.is_alive()}, FN={server_FN.is_alive()}, '
                      f'CM={server_CM.is_alive()}, blockchain={self._blockchain_thread.is_alive()}')
                break
            time.sleep(5)

    def run_flask(self, server_FN):
        app = Flask(__name__)

        @app.route('/get_active_pools_and_count_fog_nodes', methods=['GET'])
        def get_active_pools_and_count_fog_nodes():
            if self._blockchain.is_ready():
                active_pools = self._blockchain.now_active_pools()
                active_pools[self._wallet.address] = {'params': (self._ip_pool, self._port_pool,
                                                                 self._port_cm, self._port_fn),
                                                      'fog_nodes': self._blockchain.get_count_fog_nodes()}
                return jsonify(active_pools)
            return {}

        @app.route('/register_pool', methods=['POST'])
        def register_pool():
            ip = request.remote_addr
            address, port_pool, port_cm, port_fn = request.json
            append_pool_host(address, ip, port_pool, port_cm, port_fn)
            return jsonify()

        @app.route('/get_active_pools', methods=['GET'])
        def get_active_pools():
            active_pools = self._blockchain.all_active_pools()
            if not self._blockchain.is_ready() and self._wallet.address in active_pools:
                active_pools.pop(self._wallet.address)

            response = {}
            for key, item in active_pools.items():
                response[key] = item['params']
            return jsonify(response)

        @app.route('/get_active_count_fog_nodes', methods=['GET'])
        def get_active_count_fog_nodes():
            return jsonify(server_FN.get_count_workers())

        @app.route('/get_active_fog_nodes', methods=['GET'])
        def get_active_fog_nodes():
            return jsonify(server_FN.get_workers())

        """
        @app.route('/send_new_block', methods=['POST'])
        def send_new_block():
            self._blockchain.update_new_block(request.json)
            return jsonify()
        """

        @app.route('/get_block/<int:number_block>', methods=['GET'])
        def get_block(number_block):
            return jsonify(self._blockchain.get_block(number_block))

        @app.route('/get_genesis_time', methods=['GET'])
        def get_genesis_time():
            return jsonify(self._blockchain.get_genesis_time())

        @app.route('/get_my_ip', methods=['GET'])
        def get_my_ip():
            return jsonify(request.remote_addr)

        @app.route('/new_transaction', methods=['POST'])
        def new_transaction():
            data = request.json
            if not all([key in data.keys() for key in ['sender', 'count', 'date']]):
                return jsonify({'error': 'new_transaction required parameters are not specified: sender, count, date'})

            if 'data' not in data:
                data['data'] = None
            if 'owner' not in data:
                data['owner'] = None

            self._blockchain.new_transaction(sender=data['sender'], owner=data['owner'], count=data['count'],
                                             data=data['data'], date=data['date'])
            return jsonify()

        @app.route('/send_replica', methods=['POST'])
        def send_replica():
            data = request.data
            with open(get_path(f'data/pool/waiting_replicas/{sha3_256(data).hexdigest()}'), 'wb') as f:
                f.write(data)
            return jsonify()

        @app.route('/load_replica/<string:hash_replica>', methods=['GET'])
        def load_replica(hash_replica):
            if exists_path(f'data/pool/waiting_replicas/{hash_replica}'):
                with open(get_path(f'data/pool/waiting_replicas/{hash_replica}'), 'rb') as f:
                    return Response(f.read())
            # Запрос у активных фогов
            for id_fog_node in self._blockchain.get_fog_nodes():
                if self._blockchain.get_exist_replica_in_fog_node(id_fog_node, hash_replica):
                    response = self._blockchain.get_replica_in_fog_node(id_fog_node, hash_replica)
                    if response[1] == b'' and \
                            self._blockchain.get_size_replica_in_fog_node(id_fog_node, hash_replica) is not None:
                        return response[1]
                    elif response[1] != b'':
                        return response[1]
            abort(404)

        @app.route('/get_balance/<address>', methods=['GET'])
        def get_balance(address):
            return jsonify(self._blockchain.get_balance(address))

        @app.route('/get_free_balance/<address>', methods=['GET'])
        def get_occupied(address):
            address_normal = self._blockchain._dns.find_address(address)
            if address_normal:
                return jsonify({'status': 0, 'status_text': 'success',
                                'amount_free_balance': self._blockchain.get_balance(
                                    address_normal) - self._blockchain.get_occupied(
                                    address_normal)})
            return jsonify(send_status_code(100, f'Parameter "address" - {address} is not valid'))

        app.run(host='0.0.0.0', port=self._port_pool)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-ppl', '--port_pool', default=POOL_PORT, type=int, help='port to listen pool')
    parser.add_argument('-pcm', '--port_cm', default=POOL_CM_PORT, type=int,
                        help='port to listen pool clients manager')
    parser.add_argument('-pfn', '--port_fn', default=POOL_FN_PORT, type=int, help='port to listen pool fog nodes')

    args = parser.parse_args()

    mfn = ManagerFogNodes(cpu_count=1)
    if not exists_path('data/pool/key'):
        mfn.add_fog_node()
        private_key = LoadJsonFile('data/fog_nodes/key').as_list()[-1]
        SaveJsonFile('data/pool/key', private_key)
    else:
        private_key = LoadJsonFile('data/pool/key').as_string()
    pool = Pool(private_key=private_key, port_pool=args.port_pool, port_cm=args.port_cm, port_fn=args.port_fn)
    pool.start()
