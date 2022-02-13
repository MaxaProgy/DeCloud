from blockchain import Blockchain
from dctp1 import ServerDCTP, send_status_code

POOL_PORT = 8000


class Pool:
    def __init__(self, private_key):
        self._blockchain = Blockchain()
        self._private_key = private_key
        self.run()

    def run(self):
        server = ServerDCTP(POOL_PORT)

        @server.method('new_transaction')
        def new_transaction(data):
            self._blockchain.new_transaction(data['name'], data['hash_list'])

        @server.method('is_exist_replica')
        def is_exist_replica(data):
            if not self._blockchain.is_exist_replica(data['hash_list']):
                return send_status_code(100)
        server.start()
