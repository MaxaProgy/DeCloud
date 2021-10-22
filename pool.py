from blockchain import Blockchain
from dctp import ServerDCTP


class Pool:
    def __init__(self, port):
        self._blockchain = Blockchain()
        self._port = port

    def run(self):
        server = ServerDCTP(self._port)

        @server.method('new_transaction')
        def new_transaction(data):
            # Регистрируем транзакцию в блокчейне
            self._blockchain.new_transaction(data['name'], data['hash_list'])

        server.start()


if __name__ == "__main__":
    pool = Pool(2222)
    pool.run()
