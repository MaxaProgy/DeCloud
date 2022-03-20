import time
from argparse import ArgumentParser
from threading import Thread
from _pysha3 import keccak_256 as sha3_256
from multiprocessing import Process
from flask import Flask, jsonify, request
from blockchain import Blockchain
from dctp import ServerDCTP, send_status_code
from fog_nodes_manager import ManagerFogNodes
from utils import exists_path, get_path, append_pool_host, LoadJsonFile, get_my_ip
from variables import POOL_PORT, POOL_CM_PORT, POOL_FN_PORT, POOL_ROOT_IP
from wallet import Wallet


class Pool(Process):
    def __init__(self, port_pool=POOL_PORT, port_cm=POOL_CM_PORT, port_fn=POOL_FN_PORT):
        super().__init__()
        if not exists_path('data/pool/key'):
            self._wallet = Wallet()
            self._wallet.save_private_key('data/pool/key')
            print(f'Create POOL {self._wallet.address}')
        else:
            self._wallet = Wallet(LoadJsonFile('data/pool/key').as_list()[0])

        self._port_cm = port_cm
        self._port_fn = port_fn
        self._port_pool = port_pool
        self.active_cm = {}
        self._active_pools = {}
        self._blockchain_thread = None

    @property
    def _blockchain(self):
        while self._blockchain_thread is None or not self._blockchain_thread.is_alive():
            time.sleep(0.1)
        return self._blockchain_thread

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

        # получаем ip нашего пула
        self._ip_pool = get_my_ip()

        self._blockchain_thread = Blockchain(self, server_FN, self._wallet, self._ip_pool,
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

        app.run(host='0.0.0.0', port=self._port_pool)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-ppl', '--port_pool', default=POOL_PORT, type=int, help='port to listen pool')
    parser.add_argument('-pcm', '--port_cm', default=POOL_CM_PORT, type=int,
                        help='port to listen pool clients manager')
    parser.add_argument('-pfn', '--port_fn', default=POOL_FN_PORT, type=int, help='port to listen pool fog nodes')

    args = parser.parse_args()

    pool = Pool(port_pool=args.port_pool, port_cm=args.port_cm, port_fn=args.port_fn)
    pool.start()
