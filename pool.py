import time
from argparse import ArgumentParser
from threading import Thread
import requests
from _pysha3 import keccak_256 as sha3_256
from multiprocessing import Process
from flask import Flask, jsonify, request
from blockchain import Blockchain
from dctp import ServerDCTP, send_status_code
from fog_nodes_manager import ManagerFogNodes
from utils import exists_path, get_path, append_pool_host, LoadJsonFile, get_pools_host, get_my_ip, SaveJsonFile, \
    print_info
from variables import POOL_PORT, POOL_CM_PORT, POOL_FN_PORT, POOL_ROOT_IP
from wallet import Wallet


class Pool(Process):
    def __init__(self, port_pool=POOL_PORT, port_cm=POOL_CM_PORT, port_fn=POOL_FN_PORT):
        super().__init__()
        if not exists_path('data/pool/pools_host'):
            SaveJsonFile('data/pool/pools_host', {})

        if not exists_path('data/pool/key'):
            self._wallet = Wallet()
            self._wallet.save_private_key('data/pool/key')
            print(f'Create POOL {self._wallet.address}')
        else:
            self._wallet = Wallet(LoadJsonFile('data/pool/key').as_list()[0])

        self._ip = get_my_ip()
        self._port_cm = port_cm
        self._port_fn = port_fn
        self._port_pool = port_pool
        # append_pool_host(self._wallet.address, self._ip, port_pool, port_cm, port_fn)
        self.active_cm = {}
        self._active_pools = {self._wallet.address: (self._ip, self._port_pool, self._port_cm, self._port_fn)}

    def get_active_pools(self):
        return self._active_pools.copy()

    def is_root_pool(self):
        return self._ip == POOL_ROOT_IP and self._port_pool == POOL_PORT

    def run(self):
        self.mfn = ManagerFogNodes(cpu_count=1)
        self.mfn.load_fog_nodes('data/pool/key')

        server_CM = ServerDCTP(self._port_cm)

        @server_CM.method('register_pool')
        def register_pool(json, data):
            if json['worker_id'] in self.active_cm:
                self.active_cm[json['worker_id']].add(json['address'])
            else:
                self.active_cm[json['worker_id']] = {json['address']}

        @server_CM.method('send_replica')
        def send_replica(json, data):
            with open(get_path(f'data/pool/waiting_replicas/{sha3_256(data).hexdigest()}'), 'wb') as f:
                f.write(data)

        @server_CM.method('commit_replica')
        def commit_replica(json, data):
            if not self._blockchain.new_transaction(sender=json['address'], data=json['hash']):
                return send_status_code(100)

        @server_CM.method('get_occupied')
        def get_occupied(json, data):
            return {'occupied': self._blockchain.get_occupied(json['address'])}

        @server_CM.method('get_info_object')
        def get_info_object(json, data):
            return {'info': self._blockchain.get_info_object(json['address'], json['id_object'])}

        server_CM.start()

        server_FN = ServerDCTP(self._port_fn)

        @server_FN.method('connect_valid_client')
        def connect_valid_client(json):
            return Wallet.check_valid_address(json['address'])

        @server_FN.method('get_balance')
        def get_balance(json, data):
            return {'amount': self._blockchain.get_balance(json['address'])}

        server_FN.start()

        # tun Flask - обмен данными между пулами
        flask_thread = Thread(target=self.run_flask, args=[server_FN])
        flask_thread.start()

        time.sleep(5)

        self._blockchain = Blockchain(self, server_FN)
        self._blockchain.start()

        print(f'Start POOL {self._wallet.address}')

        while True:
            if not (flask_thread.is_alive() and server_FN.is_alive()
                    and server_CM.is_alive() and self._blockchain.is_alive()):
                print(f'Error POOL {self._wallet.address} flask={flask_thread.is_alive()}, FN={server_FN.is_alive()}, '
                      f'CM={server_CM.is_alive()}, blockchain={self._blockchain.is_alive()}')
                break
            pools = get_pools_host('data/pool/pools_host')
            if not pools:
                pools[''] = (POOL_ROOT_IP, POOL_PORT, POOL_CM_PORT, POOL_FN_PORT)
            pools_new = {}
            for key, item in list(pools.items()):
                try:
                    # добавить корутины
                    response = requests.post(f'http://{item[0]}:{item[1]}/register_pool_and_get_active_pools',
                                             json=(self._wallet.address, self._port_pool,
                                                   self._port_cm, self._port_fn)).json()
                    for key_response, item_response in response.items():
                        pools_new[key_response] = item_response
                    if key != '':
                        self._active_pools[key] = item
                except:
                    if key != "":
                        pools_new[key] = pools[key]
                    if key in self._active_pools:
                        self._active_pools.pop(key)

            if self._wallet.address in pools_new:
                self._active_pools[self._wallet.address] = pools_new[self._wallet.address]
                pools_new.pop(self._wallet.address)
            SaveJsonFile('data/pool/pools_host', pools_new)

            print_info("All pools", pools_new)
            print_info("Active pools", self._active_pools)
            print_info('Active fog nodes', server_FN.get_workers())
            time.sleep(10)

    def run_flask(self, server_FN):
        app = Flask(__name__)

        @app.route('/register_pool_and_get_active_pools', methods=['POST'])
        def register_pool_and_get_active_pools():
            data = request.json
            ip = request.remote_addr
            address, port_pool, port_cm, port_fn = data
            self._active_pools[address] = (ip, port_pool, port_cm, port_fn)
            if address != self._wallet.address:
                append_pool_host(address, ip, port_pool, port_cm, port_fn)
            return jsonify(self._active_pools)

        @app.route('/get_active_pools', methods=['GET'])
        def get_active_pools():
            return jsonify(self._active_pools)

        @app.route('/get_active_count_fog_nodes', methods=['GET'])
        def get_active_count_fog_nodes():
            return jsonify(len(server_FN.get_workers()))

        @app.route('/get_active_fog_nodes', methods=['GET'])
        def get_active_fog_nodes():
            return jsonify(server_FN.get_workers())

        @app.route('/send_new_block', methods=['POST'])
        def send_new_block():
            self._blockchain.update_new_block(request.json)
            return jsonify()

        @app.route('/get_block/<int:number_block>', methods=['GET'])
        def get_block(number_block):
            return jsonify(self._blockchain.get_block(number_block))

        @app.route('/get_genesis_time', methods=['GET'])
        def get_genesis_time():
            return jsonify(self._blockchain.get_genesis_time())

        app.run(host='127.0.0.1', port=self._port_pool)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-ppl', '--port_pool', default=POOL_PORT, type=int, help='port to listen pool')
    parser.add_argument('-pcm', '--port_cm', default=POOL_CM_PORT, type=int,
                        help='port to listen pool clients manager')
    parser.add_argument('-pfn', '--port_fn', default=POOL_FN_PORT, type=int, help='port to listen pool fog nodes')

    args = parser.parse_args()

    pool = Pool(port_pool=args.port_pool, port_cm=args.port_cm, port_fn=args.port_fn)
    pool.start()
