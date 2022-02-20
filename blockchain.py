import hashlib
import json as _json
import datetime
import os
import pickle
import time
from threading import Thread

from utils import exists_path, get_path, get_pools_address


class Blockchain(Thread):
    def __init__(self, server_fn):
        super().__init__()
        self._now_block_number = 0
        self._transactions = []
        self._blocks = []
        self.server_fn = server_fn
        if exists_path(dirs=['data', 'pool'], file='waiting_transaction'):
            with open(get_path(dirs=['data', 'pool'], file='waiting_transaction'), 'rb') as f:
                self._transactions = pickle.load(f)
        self._file_blockchain = get_path(dirs=['data', 'pool'], file='waiting_transaction')

    def get_now_block_number(self):
        return self._now_block_number

    def new_transaction(self, sender, owner=None, count=0, data=None):
        if data:
            path = get_path(dirs=['data', 'pool', 'waiting_replicas'], file=data)
            if not os.path.exists(path):
                return False
            count = os.path.getsize(path)

            with open(path, 'r') as f:
                list_hashes_file = _json.loads(f.readline())[2]
                for hash in list_hashes_file:
                    path = get_path(dirs=['data', 'pool', 'waiting_replicas'], file=hash)
                    if not os.path.exists(path):
                        return False
                    count += os.path.getsize(path)

        self._transactions.append({'sender': sender, 'owner': owner, 'count': count,
                                   'data': data, 'date': datetime.datetime.utcnow().timestamp()})
        self._save_transactions()
        return True

    """def is_exist_replica(self, hash_replica):
        for name in self._transactions:
            if hash_replica in self._transactions[name]:
                return True
        return False"""

    def run(self):
        if self._now_block_number == 0:
            hash_last = self._save_block({'number': self._now_block_number,
                                          'date': datetime.datetime.utcnow().timestamp(),
                                          'transactions': [], 'hash_last': 0})
        while True:
            time.sleep(10)
            fn_workers = list(self.server_fn.get_workers()) + get_pools_address()
            hash_last_cut = hash_last[-len(fn_workers[0]):]
            nearest = fn_workers[0]
            for worker in fn_workers:
                if (hash_last_cut >= worker > nearest) or (hash_last_cut <= worker < nearest):
                    nearest = worker

            hash_last = self._save_block({'number': self._now_block_number,
                                          'date': datetime.datetime.utcnow().timestamp(),
                                          'recipient': nearest,
                                          'amount': 100,
                                          'transactions': self._transactions,
                                          'hash_last': hash_last})

    def _save_transactions(self):
        with open(self._file_blockchain, 'wb') as f:
            pickle.dump(self._transactions, f)

    def _save_block(self, data):
        self._now_block_number += 1
        hash_last = hex(int.from_bytes(hashlib.sha3_256(bytes(_json.dumps(data),
                                                              'utf-8')).digest(), 'big'))[2:]
        with open(get_path(dirs=['data', 'pool', 'waiting_replicas'], file=hash_last), 'w') as f:
            f.write(_json.dumps(data))

        self._transactions = []
        self._save_transactions()
        print(f'Create block number: {self._now_block_number} - hash {hash_last}')
        return hash_last
