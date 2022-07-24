import time
from argparse import ArgumentParser
from threading import Thread
from _pysha3 import keccak_256 as sha3_256
from multiprocessing import Process
from blockchain import Blockchain
from dctp import ServerDCTP, send_status_code
from fog_nodes_manager import ManagerFogNodes
from utils import exists_path, get_path, append_pool_host, LoadJsonFile, SaveJsonFile, print_info
from variables import POOL_PORT, POOL_CM_PORT, POOL_FN_PORT
from wallet import Wallet
import json as _json


class Pool(Process):
    def __init__(self, private_key, port_pool=POOL_PORT, port_cm=POOL_CM_PORT, port_fn=POOL_FN_PORT, port_app=None):
        super().__init__()
        self._wallet = Wallet(private_key)
        self._port_cm = port_cm
        self._port_fn = port_fn
        self._port_app = port_app
        self._port_pool = port_pool
        self._active_pools = {}
        self._blockchain_thread = None
        self.stoping = False

    @property
    def _blockchain(self):
        while self._blockchain_thread is None or not self._blockchain_thread.is_alive():
            time.sleep(0.1)
        return self._blockchain_thread

    def run(self):
        if not Wallet.check_valid_address(self._wallet.address):
            raise Exception(f'Pool address {self._wallet.address} is not valid')
        if self._port_app:
            server_APP = ServerDCTP(self._port_app)

            @server_APP.method('stop')
            def stop(request):
                self.server_CM.stop()
                self.server_FN.stop()
                self._blockchain_thread.stop()

                while sum([thread.is_alive() for thread in
                           (self.server_CM, self.server_FN, self._blockchain_thread)]) != 0:
                    time.sleep(0.1)
                self.stoping = True
                exit = Thread(target=self.server_APP.stop)
                exit.start()

            server_APP.start()
        else:
            server_APP = None
        self.server_APP = server_APP

        server_CM = ServerDCTP(self._port_cm)

        @server_CM.method('send_replica')
        def send_replica(request):
            with open(get_path(f'data/pool/waiting_replicas/{sha3_256(request.data).hexdigest()}'), 'wb') as f:
                f.write(request.data)

        @server_CM.method('commit_replica')
        def commit_replica(request):
            if not all([key in request.json for key in ['data']]):
                return send_status_code(100, 'Required parameters are not specified: data')

            code, text = self._blockchain.new_transaction(sender=request.id_client, data=request.json['data'],
                                                          date=self._blockchain.sync_utcnow_timestamp(), is_cm=True)
            return send_status_code(code, text)

        @server_CM.method('new_transaction')
        def new_transaction(request):
            if not all([key in request.json for key in ['sender', 'owner', 'count']]):
                return send_status_code(100, 'Required parameters are not specified: sender, owner, count')

            request.json['sender'] = request.json['sender'].lstrip().rstrip()
            request.json['owner'] = request.json['owner'].lstrip().rstrip()
            if request.json['sender'] == request.json['owner']:
                return send_status_code(100, 'Are you stupid? why send byteEx yourself.')

            if type(request.json['count']) == int:
                if request.json['count'] <= 0:
                    return send_status_code(100, 'Required parameter "count" must be greater than zero')
            else:
                return send_status_code(100, 'Required parameter "count" must be a number')

            code, text = self._blockchain.new_transaction(sender=request.json['sender'], owner=request.json['owner'],
                                                          count=request.json['count'],
                                                          date=self._blockchain.sync_utcnow_timestamp(), is_cm=True)
            return send_status_code(code, text)

        @server_CM.method('get_occupied')
        def get_occupied(request):
            return {'occupied': self._blockchain.get_occupied(request.id_client)}

        @server_CM.method('get_info_object')
        def get_info_object(request):
            return {'info': self._blockchain.get_info_object(request.id_client, request.json['id_object'])}

        @server_CM.method('get_all_ns')
        def get_all_ns(request):
            return {'all_ns': self._blockchain._dns.get_all_ns(request.id_client)}

        @server_CM.method('registration_domain_name')
        def registration_domain_name(request):
            if not all([key in request.json for key in ['address', 'name']]):
                return send_status_code(100, 'Required parameters are not specified: address, name')
            if type(request.json['name']) != str or not request.json['name'].strip():
                return send_status_code(100, 'Parameter "name" is not valid')

            replica = ['ns', request.json['name'], request.id_client]
            hash_replica = sha3_256(bytes(_json.dumps(replica), 'utf-8')).hexdigest()
            SaveJsonFile(f'data/pool/waiting_replicas/{hash_replica}', replica)
            code, text = self._blockchain.new_transaction(sender=request.id_client, data=hash_replica,
                                                          date=self._blockchain.sync_utcnow_timestamp(), is_cm=True)
            return send_status_code(code, text)

        @server_CM.method('check_valid_address')
        def check_valid_address(request):
            return {'address_normal': self._blockchain._dns.find_address(request.id_client)}

        server_CM.start()
        self.server_CM = server_CM

        server_FN = ServerDCTP(self._port_fn)

        @server_FN.method('connect_valid_client')
        def connect_valid_client(request):
            return Wallet.check_valid_address(request.id_worker)

        @server_FN.method('on_connected')
        def on_connected(request):
            response = server_FN.request(id_worker=request.id_worker, method='get_hash_replicas').json
            if all([key in response for key in ['hash_replicas', 'size_fog_node']]):
                self._blockchain.add_fog_node(id_fog_node=request.id_worker,
                                              data={'hash_replicas': response['hash_replicas'],
                                                    'size_fog_node': response['size_fog_node']})

        @server_FN.method('on_disconnected')
        def on_disconnected(request):
            self._blockchain.del_fog_node(request.id_worker)

        @server_FN.method('get_balance')
        def get_balance(request):
            return {'amount': self._blockchain.get_balance(request.id_client)}

        server_FN.start()
        self.server_FN = server_FN

        # tun Flask - обмен данными между пулами
        self.flask_thread = Thread(target=self.run_flask, args=[server_FN])
        self.flask_thread.setDaemon(True)
        self.flask_thread.start()

        # получаем ip нашего пула
        self._blockchain_thread = Blockchain(server_FN, server_APP, self._wallet,
                                             self._port_pool, self._port_cm, self._port_fn)
        self._blockchain_thread.start()

        while not self.stoping:

            if not (self.flask_thread and self.flask_thread.is_alive() and server_FN.is_alive()
                    and server_CM.is_alive() and self._blockchain_thread.is_alive()):
                try:
                    print_info(f'Error POOL {self._wallet.address}')
                    print_info(f'FN={server_FN} {server_FN.is_alive()}')
                    print_info(f'CM={server_CM} {server_CM.is_alive()}')
                    print_info(f'blockchain={self._blockchain_thread.is_alive()}')
                    print_info(f'flask={self.flask_thread}')
                    print_info(f'flask={self.flask_thread.is_alive()}')
                    print_info()
                except:
                    pass

            time.sleep(1)

    def run_flask(self, server_FN):
        from flask import Flask, jsonify, request, abort, Response
        from gevent.pywsgi import WSGIServer

        app = Flask(__name__)

        @app.route('/get_my_ip', methods=['GET'])
        def get_my_ip():
            return jsonify(request.remote_addr)

        @app.route('/get_sync_time', methods=['GET'])
        def get_sync_time():
            return jsonify(self._blockchain.sync_utcnow_timestamp())

        @app.route('/get_block_number', methods=['GET'])
        def get_block_number():
            return jsonify(self._blockchain.get_block_number())

        @app.route('/sync_pools', methods=['POST'])
        def sync_pools():
            try:
                address, params = _json.loads(request.data)
            except:
                abort(400)

            if address in self._blockchain._all_active_pools:
                if _json.dumps(self._blockchain._all_active_pools[address]) != _json.dumps(params):
                    append_pool_host(address, *params)
            else:
                append_pool_host(address, *params)

            fog_nodes = 0
            if self._blockchain.is_ready:
                fog_nodes = self._blockchain.all_active_pools()['fog_nodes'][self._wallet.address]

            return jsonify({'address':self._wallet.address,
                            'params': self._blockchain.all_active_pools()['params'],
                            'fog_nodes': fog_nodes})

        @app.route('/active_pools', methods=['GET'])
        def active_pools():
            return jsonify(self._blockchain.all_active_pools()['params'])

        @app.route('/count_fog_nodes', methods=['GET'])
        def count_fog_nodes():
            if self._blockchain.is_ready():
                return jsonify(server_FN.get_count_workers())
            else:
                return abort(404)

        @app.route('/fog_nodes', methods=['GET'])
        def fog_nodes():
            return jsonify(server_FN.get_workers())

        @app.route('/get_block/<int:number_block>', methods=['GET'])
        def get_block(number_block):
            return jsonify(self._blockchain.get_block(number_block))

        @app.route('/get_current_winner_pool', methods=['GET'])
        def get_current_winner_pool():
            return jsonify(self._blockchain.winner_address_pool)

        @app.route('/genesis_time', methods=['GET'])
        def genesis_time():
            return jsonify(self._blockchain.get_genesis_time())

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
            # Ищем в папке waiting_replicas
            if exists_path(f'data/pool/waiting_replicas/{hash_replica}'):
                with open(get_path(f'data/pool/waiting_replicas/{hash_replica}'), 'rb') as f:
                    return Response(f.read())
            # Запрос у активных фогов
            for id_fog_node in self._blockchain.get_fog_nodes():
                if self._blockchain.get_exist_replica_in_fog_node(id_fog_node, hash_replica):
                    response = self._blockchain.get_replica_in_fog_node(id_fog_node, hash_replica)
                    if response.data == b'' and \
                            self._blockchain.get_size_replica_in_fog_node(id_fog_node, hash_replica) is not None:
                        return response.json
                    elif response.data != b'':
                        return response.json
            abort(404)

        # Баланс кошлелка <address>
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
        #pool_server = WSGIServer(('0.0.0.0', self._port_pool), app)
        #pool_server.serve_forever()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-ppl', '--port_pool', default=POOL_PORT, type=int, help='port to listen pool')
    parser.add_argument('-pcm', '--port_cm', default=POOL_CM_PORT, type=int,
                        help='port to listen pool clients manager')
    parser.add_argument('-pfn', '--port_fn', default=POOL_FN_PORT, type=int, help='port to listen pool fog nodes')

    args = parser.parse_args()

    mfn = ManagerFogNodes(cpu_count=1)
    if not exists_path('data/pool/key'):
        wallet = mfn.create_fog_node()
        mfn.start_fog_node(wallet)
        SaveJsonFile('data/pool/key', wallet.private_key)
        private_key = wallet.private_key
    else:
        private_key = LoadJsonFile('data/pool/key').as_string()
    pool = Pool(private_key=private_key, port_pool=args.port_pool, port_cm=args.port_cm, port_fn=args.port_fn)
    pool.start()
