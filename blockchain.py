from _pysha3 import keccak_256 as sha3_256
import json as _json
import datetime
import os
import pickle
import time
from threading import Thread

from utils import exists_path, get_path, get_pools_address, get_size_file
AMOUNT = 1024**2

class Blockchain(Thread):
    def __init__(self, server_fn):
        super().__init__()
        self._now_block_number = 0
        self._transactions = []
        self._blocks = []
        self.server_fn = server_fn
        self._state_address_amount = {}
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
        flag = exists_path(dirs=['data', 'pool'], file='save_data')
        path = get_path(dirs=['data', 'pool'], file='save_data')
        if flag:
            with open(path, 'r') as f:
                hash_last = f.readline()
                genesis_time = float(f.readline())
                self._now_block_number = int(f.readline()) + 1
            self._load_state_address_amount()

        else:
            hash_last = '0'
            genesis_time = datetime.datetime.utcnow().timestamp()
            with open(path, 'w') as f:
                f.write(hash_last+'\n'+str(genesis_time)+'\n0')

        while True:
            sleep_sec = genesis_time + (60 * self._now_block_number) - datetime.datetime.utcnow().timestamp()
            if sleep_sec < 0:
                sleep_sec = 0
            time.sleep(sleep_sec)

            members = list(self.server_fn.get_workers()) + get_pools_address()

            hash_last_cut = hash_last[-len(members[0]):]
            #print(hash_last_cut)
            nearest = members[0]
            for member in members:
                if (hash_last_cut >= member > nearest) or (hash_last_cut <= member < nearest):
                    nearest = member
            self._state_address_amount[nearest] = self._state_address_amount.get(nearest, 0) + AMOUNT
            #for key in self._state_address_amount:
            #    print(key, self._state_address_amount[key])
            state_size_transaction = {}
            transactions = self._transactions.copy()
            self._transactions = []
            for i in range(len(transactions) - 1, -1, -1):
                path = get_path(dirs=['data', 'pool', 'waiting_replicas'],
                                file=transactions[i]['data'])
                sender = transactions[i]['sender']
                size = os.path.getsize(path)
                with open(path, 'r') as f:
                    hashes_replica = _json.loads(f.readline())[2]
                    for hash in hashes_replica:
                       size += get_size_file(dirs=['data', 'pool', 'waiting_replicas'], file=hash)
                state_size_transaction[sender] = state_size_transaction.get(sender, 0)
                size_amount = self._state_address_amount.get(sender, 0)
                if size_amount < state_size_transaction[sender] + size:
                    transactions.pop(i)
                    for hash in hashes_replica:
                        os.remove(get_path(dirs=['data', 'pool', 'waiting_replicas'], file=hash))
                    os.remove(path)
                else:
                    state_size_transaction[sender] += size

            hash_last = self._save_block({'number': self._now_block_number,
                                          'date': datetime.datetime.utcnow().timestamp(),
                                          'recipient': nearest,
                                          'amount': AMOUNT,
                                          'transactions': transactions,
                                          'hash_last': hash_last})
            with open(path, 'w') as f:
                f.write(hash_last+'\n'+str(genesis_time) +'\n'+str(self._now_block_number))
            if nearest in list(self.server_fn.get_workers()):
                self.server_fn.request(nearest, 'update_balance', {'amount': self._state_address_amount.get(nearest, 0)})
            self._now_block_number += 1

    def get_balance(self, address):
        if address not in self._state_address_amount.keys():
            return 0
        return self._state_address_amount[address]

    def _save_transactions(self):
        with open(self._file_blockchain, 'wb') as f:
            pickle.dump(self._transactions, f)

    def _load_state_address_amount(self):
        with open(get_path(dirs=['data', 'pool'], file='state_address_amount'), 'r') as f:
            self._state_address_amount = _json.loads(f.read())

    def _save_state_address_amount(self):
        with open(get_path(dirs=['data', 'pool'], file='state_address_amount'), 'w') as f:
            f.write(_json.dumps(self._state_address_amount))

    def _save_block(self, data):
        hash_last = hex(int.from_bytes(sha3_256(bytes(_json.dumps(data),
                                                              'utf-8')).digest(), 'big'))[2:]
        with open(get_path(dirs=['data', 'pool', 'waiting_replicas'], file=hash_last), 'w') as f:
            f.write(_json.dumps(data))

        self._save_transactions()
        print(f'Create block number: {self._now_block_number} {hash_last} - payment address {data["recipient"]} = {data["amount"]}')
        self._save_state_address_amount()
        return hash_last
