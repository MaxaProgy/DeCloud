from _pysha3 import keccak_256 as sha3_256
from multiprocessing import Process

from flask import Flask

from blockchain import Blockchain
from dctp import ServerDCTP, send_status_code
from utils import exists_path, get_path, append_pool_host, LoadJsonFile, get_pools_host, get_my_ip
from variables import POOL_PORT, POOL_CM_PORT, POOL_FN_PORT
from wallet import Wallet


class Pool(Process):
    def __init__(self, port_pool=POOL_PORT, port_cm=POOL_CM_PORT, port_fn=POOL_FN_PORT):
        super().__init__()
        if not exists_path(path='data/pool/key'):
            self._wallet = Wallet()
            self._wallet.save_private_key(path='data/pool/key')
            print(f'Create POOL {self._wallet.address}')
        else:
            self._wallet = Wallet(LoadJsonFile(path='data/pool/key').as_list()[0])
        self._ip = get_my_ip()
        self._port_cm = port_cm
        self._port_fn = port_fn
        self._port_pool = port_pool
        append_pool_host(self._wallet.address, self._ip, self._port_pool, self._port_cm, self._port_fn)
        self.active_cm = {}
        self.get_active_pools()

    def get_active_pools(self):
        return get_pools_host()

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

        self._blockchain = Blockchain(self, server_CM, server_FN)
        self._blockchain.start()

        print(f'Start POOL {self._wallet.address}')

        app = Flask(__name__)

        @app.route('/you_connect', methods=['GET'])
        def you_connect():
            pass

        app.run(host='127.0.0.1', port=self._port_pool)


if __name__ == '__main__':
    pool = Pool(port_pool=3333, port_cm=3334, port_fn=3335)
    pool.start()
