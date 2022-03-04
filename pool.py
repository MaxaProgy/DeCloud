from _pysha3 import keccak_256 as sha3_256
import time
from multiprocessing import Process
from blockchain import Blockchain
from dctp import ServerDCTP, send_status_code
from utils import exists_path, get_path, POOL_CSM_PORT, POOL_FN_PORT, append_pool_host, LoadJsonFile
from wallet import Wallet


class Pool(Process):
    def __init__(self):
        super().__init__()
        if not exists_path(dirs=['data', 'pool'], file='key'):
            self._wallet = Wallet()
            self._wallet.save_private_key(dirs=['data', 'pool'], file='key')
            print(f'Create POOL {self._wallet.address}')

        else:
            self._wallet = Wallet(LoadJsonFile(dirs=['data', 'pool'], file='key').as_list()[0])
        self._ip = '127.0.0.1'
        self._port_csm = POOL_CSM_PORT
        self._port_fn = POOL_FN_PORT
        append_pool_host(self._wallet.address, self._ip, self._port_csm, self._port_fn)

    def run(self):
        server_CSM = ServerDCTP(POOL_CSM_PORT)

        @server_CSM.method('send_replica')
        def send_replica(json, data):
            with open(get_path(dirs=['data', 'pool', 'waiting_replicas'],
                               file=sha3_256(data).hexdigest()), 'wb') as f:
                f.write(data)

        @server_CSM.method('commit_replica')
        def commit_replica(json, data):
            if not self._blockchain.new_transaction(sender=json['address'], data=json['hash']):
                return send_status_code(100)

        @server_CSM.method('get_occupied')
        def get_occupied(json, data):
            return {'occupied': self._blockchain.get_occupied(json['address'])}

        @server_CSM.method('get_info_object')
        def get_info_object(json, data):
            return {'info': self._blockchain.get_info_object(json['address'], json['id_object'])}

        server_CSM.start()

        server_FN = ServerDCTP(POOL_FN_PORT)

        @server_FN.method('get_balance')
        def get_balance(json, data):
            return {'amount': self._blockchain.get_balance(json['address'])}

        server_FN.start()

        self._blockchain = Blockchain(server_FN)
        self._blockchain.start()

        print(f'Start POOL {self._wallet.address}')

        while True:
            time.sleep(5)
