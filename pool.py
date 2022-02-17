from multiprocessing import Process

from blockchain import Blockchain
from dctp1 import ServerDCTP, send_status_code
from utils import exists_path, get_path
from wallet import Wallet

POOL_PORT = 8000

def get_pools_host():
    return [['127.0.0.1', 8000]]

class Pool(Process):
    def __init__(self):
        super().__init__()
        self._blockchain = Blockchain()
        if not exists_path(dirs=['data', 'pool'], file='key'):
            self._wallet = Wallet()
            self._wallet.save_private_key(get_path(dirs=['data', 'pool'], file='key'))
            print(f'Create POOL {self._wallet.address}')
        else:
            with open(get_path(dirs=['data', 'pool'], file='key'), 'r') as f:
                self._wallet = Wallet(f.readline())

    def run(self):
        server = ServerDCTP(POOL_PORT)
        print(f'Start POOL {self._wallet.address}')

        @server.method('new_transaction')
        def new_transaction(data):
            self._blockchain.new_transaction(data['name'], data['hash_list'])

        @server.method('is_exist_replica')
        def is_exist_replica(data):
            if not self._blockchain.is_exist_replica(data['hash_list']):
                return send_status_code(100)
        @server.method('commit_replica')
        def commit_replica(data):
            pass

        server.start()
