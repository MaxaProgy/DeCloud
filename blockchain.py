import os
import pickle


class Blockchain:
    def __init__(self):
        self._file_blockchain = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'blockchain')
        if os.path.exists(self._file_blockchain):
            with open(self._file_blockchain, 'rb') as f:
                self.transaction = pickle.load(f)
        else:
            self.transaction = dict()

    def new_transaction(self, name, hash_list):
        self.transaction[name] = hash_list
        with open(self._file_blockchain, 'wb') as f:
            pickle.dump(self.transaction, f)

    def is_exist_block(self, hash_block):
        for name in self.transaction.keys():
            if hash_block in self.transaction[name]:
                return True
        return False
