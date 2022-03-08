import time
from argparse import ArgumentParser
from threading import Thread

import requests
from _pysha3 import keccak_256 as sha3_256
from multiprocessing import Process

from flask import Flask, jsonify, request

from blockchain import Blockchain
from dctp import ServerDCTP, send_status_code
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
            self._wallet.save_private_key(path='data/pool/key')
            print(f'Create POOL {self._wallet.address}')
        else:
            self._wallet = Wallet(LoadJsonFile(path='data/pool/key').as_list()[0])
        self._ip = get_my_ip()
        self._port_cm = port_cm
        self._port_fn = port_fn
        self._port_pool = port_pool
        # append_pool_host(self._wallet.address, self._ip, port_pool, port_cm, port_fn)
        self.active_cm = {}
        self._active_pools = {self._wallet.address: (self._ip, self._port_pool, self._port_cm, self._port_fn)}

    def get_active_pools(self):
        return self._active_pools

    def run(self):
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
            if not _blockchain.new_transaction(sender=json['address'], data=json['hash']):
                return send_status_code(100)

        @server_CM.method('get_occupied')
        def get_occupied(json, data):
            return {'occupied': _blockchain.get_occupied(json['address'])}

        @server_CM.method('get_info_object')
        def get_info_object(json, data):
            return {'info': _blockchain.get_info_object(json['address'], json['id_object'])}

        server_CM.start()

        server_FN = ServerDCTP(self._port_fn)

        @server_FN.method('connect_valid_client')
        def connect_valid_client(json):
            return Wallet.check_valid_address(json['address'])

        @server_FN.method('get_balance')
        def get_balance(json, data):
            return {'amount': _blockchain.get_balance(json['address'])}

        server_FN.start()

        _blockchain = Blockchain(self, server_CM, server_FN)
        _blockchain.start()

        flask_thread = Thread(target=self.run_flask, args=[server_FN])
        flask_thread.start()
        print(f'Start POOL {self._wallet.address}')

        while True:
            if not (flask_thread.is_alive() and server_FN.is_alive()
                    and server_CM.is_alive() and _blockchain.is_alive()):
                print(f'Error POOL {self._wallet.address}')
                break
            pools = get_pools_host('data/pool/pools_host')
            if not pools and (self._ip != POOL_ROOT_IP or self._port_pool != POOL_PORT):
                pools[''] = (POOL_ROOT_IP, POOL_PORT, POOL_CM_PORT, POOL_FN_PORT)
            pools_new = {}
            for key, item in list(pools.items()):
                if key == self._wallet.address:
                    continue
                try:
                    # добавить карутины
                    response = requests.get(f'http://{item[0]}:{item[1]}/get_pools_host',
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
                pools_new.pop(self._wallet.address)
            SaveJsonFile('data/pool/pools_host', pools_new)

            print_info("All pools", pools_new)
            print_info("Active pools", self._active_pools)
            print_info('Active fog nodes', server_FN.get_workers())
            time.sleep(10)

    def run_flask(self, server_FN):
        app = Flask(__name__)

        @app.route('/get_pools_host', methods=['GET'])
        def get_pools_host():
            data = request.json
            ip = request.remote_addr
            # print(55555555555555555, data)
            address, port_pool, port_cm, port_fn = data
            if address != "":
                self._active_pools[address] = (ip, port_pool, port_cm, port_fn)
                if address != self._wallet.address:
                    append_pool_host(address, ip, port_pool, port_cm, port_fn)
            return jsonify(self._active_pools)

        @app.route('/get_active', methods=['GET'])
        def get_active():
            return jsonify(self._active_pools)

        @app.route('/get_count_fog_nodes', methods=['GET'])
        def get_count_fog_nodes():
            return jsonify(len(server_FN.get_workers()))

        app.run(host='127.0.0.1', port=self._port_pool)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-ppl', '--port_pool',  default=POOL_PORT, type=int, help='port to listen pool')
    parser.add_argument('-pcm', '--port_cm',  default=POOL_CM_PORT, type=int,
                        help='port to listen pool clients manager')
    parser.add_argument('-pfn', '--port_fn',  default=POOL_FN_PORT, type=int, help='port to listen pool fog nodes')

    args = parser.parse_args()
    pool = Pool(port_pool=args.port_pool, port_cm=args.port_cm, port_fn=args.port_fn)
    pool.start()
