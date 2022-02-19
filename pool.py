import hashlib
from multiprocessing import Process

from blockchain import Blockchain
from dctp1 import ServerDCTP
from utils import exists_path, get_path
from wallet import Wallet

POOL_PORT = 4909


def get_pools_host():
    return [['127.0.0.1', POOL_PORT]]


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

        @server.method('send_replica')
        def send_replica(json, data):
            print(id(data))
            print(get_path(dirs=['data', 'pool', 'waiting_replicas'],
                           file=hashlib.sha3_256(data).hexdigest()))
            with open(get_path(dirs=['data', 'pool', 'waiting_replicas'],
                               file=hashlib.sha3_256(data).hexdigest()), 'wb') as f:
                print(3333444)
                f.write(data)

        @server.method('commit_replica')
        def commit_replica(json, data):
            pass

        server.start()
