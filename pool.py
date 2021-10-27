from blockchain import Blockchain
from dctp import ServerDCTP, send_status_code


class Pool:
    def __init__(self, port):
        self._blockchain = Blockchain()
        self._port = port

    def run(self):
        server = ServerDCTP(self._port)

        @server.method('new_transaction')
        def new_transaction(data):
            self._blockchain.new_transaction(data['name'], data['hash_list'])

        @server.method('is_exist_block')
        def is_exist_block(data):
            if not self._blockchain.is_exist_block(data['hash_list']):
                return send_status_code(100)
        server.start()


if __name__ == "__main__":
    pool = Pool(8888)
    pool.run()
