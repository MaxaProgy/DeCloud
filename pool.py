import hashlib
import time
from multiprocessing import Process
from blockchain import Blockchain
from dctp1 import ServerDCTP, send_status_code
from utils import exists_path, get_path, POOL_CSM_PORT, POOL_FN_PORT, set_pools_fn_host, set_pools_csm_host
from wallet import Wallet


class Pool(Process):
    def __init__(self):
        super().__init__()


        if not exists_path(dirs=['data', 'pool'], file='key'):
            self._wallet = Wallet()
            self._wallet.save_private_key(get_path(dirs=['data', 'pool'], file='key'))
            print(f'Create POOL {self._wallet.address}')

        else:
            with open(get_path(dirs=['data', 'pool'], file='key'), 'r') as f:
                self._wallet = Wallet(f.readline())
        self._ip = '127.0.0.1'
        self._port_csm = POOL_CSM_PORT
        self._port_fn = POOL_FN_PORT
        set_pools_fn_host(self._wallet.address, self._ip, self._port_fn)
        set_pools_csm_host(self._wallet.address, self._ip, self._port_csm)

    def run(self):
        server_CSM = ServerDCTP(POOL_CSM_PORT)

        @server_CSM.method('send_replica')
        def send_replica(json, data):
            with open(get_path(dirs=['data', 'pool', 'waiting_replicas'],
                               file=hashlib.sha3_256(data).hexdigest()), 'wb') as f:
                f.write(data)

        @server_CSM.method('commit_replica')
        def commit_replica(json, data):
            if not self._blockchain.new_transaction(sender=json['address'], data=json['hash']):
                return send_status_code(100)

        server_CSM.start()

        server_FN = ServerDCTP(POOL_FN_PORT)

        server_FN.start()

        self._blockchain = Blockchain(server_FN)
        self._blockchain.start()

        print(f'Start POOL {self._wallet.address}')

        while True:
            time.sleep(5)
            # print(self._blockchain.get_now_block_number())
