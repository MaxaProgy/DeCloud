from _pysha3 import keccak_256 as sha3_256
import json as _json
import datetime
import os
import pickle
import time
from threading import Thread

from utils import exists_path, get_path, get_pools_address, get_size_file, print_error, \
    print_info, LoadJsonFile, SaveJsonFile

AMOUNT = 1024 ** 2


class ClientState:
    def __init__(self, address):
        self._address = address
        self._state_client = {'all_balance': 0,
                              'occupied_balance': 0,
                              'objects': {}}
        self._dirs = ['data', 'pool', 'state', *[self._address[i:i + 2] for i in range(0, len(self._address) - 2, 2)]]
        self._file = self._address[-2:]
        self._load_state()

    def _load_state(self):
        if not exists_path(dirs=self._dirs, file=self._file):
            return
        self._state_client = LoadJsonFile(dirs=self._dirs, file=self._file).as_dict()

    def _save_state(self):
        SaveJsonFile(dirs=self._dirs, file=self._file, data=self._state_client)

    def add_object(self, id_object, size):
        self._state_client['objects'][id_object] = {'date': datetime.datetime.utcnow().timestamp(),
                                                    'size': size}
        self._save_state()

    def info_object(self, id_object):
        if id_object in self._state_client['objects'].keys():
            return self._state_client['objects'][id_object]
        return {}

    @property
    def all_balance(self):
        return self._state_client['all_balance']

    @all_balance.setter
    def all_balance(self, amount):
        self._state_client['all_balance'] = amount
        self._save_state()

    @property
    def occupied_balance(self):
        return self._state_client['occupied_balance']

    @occupied_balance.setter
    def occupied_balance(self, amount):
        self._state_client['occupied_balance'] = amount
        self._save_state()


class Blockchain(Thread):
    def __init__(self, server_fn):
        super().__init__()
        self._now_block_number = 0  # Номер текущего блока
        self._transactions = []  # Список всех транзакций за один блок
        self.server_fn = server_fn  # DCTP server для общения с FogNode

        if exists_path(dirs=['data', 'pool'], file='waiting_transaction'):
            # Загружаем транзакции, которые ожидают обработки
            with open(get_path(dirs=['data', 'pool'], file='waiting_transaction'), 'rb') as f:
                self._transactions = pickle.load(f)

    def new_transaction(self, sender, owner=None, count=0, data=None):
        # Создание новой транзакции
        if data:  # При наличии контрольной реплики со всеми хешами файла
            path = get_path(dirs=['data', 'pool', 'waiting_replicas'], file=data)
            if not os.path.exists(path):  # Если нет контрольной реплики, то не создаем транзакцию
                print_error('Error Not main replica', data)
                return False
            count = os.path.getsize(path)

            data_file = LoadJsonFile(dirs=['data', 'pool', 'waiting_replicas'], file=data).as_list()
            if len(data_file) == 3:
                for hash in data_file[2]:
                    path = get_path(dirs=['data', 'pool', 'waiting_replicas'], file=hash)
                    if not os.path.exists(path):
                        print_error('Not replica', hash)
                        return False
                    count += os.path.getsize(path)

        self._transactions.append({'sender': sender, 'owner': owner, 'count': count,
                                   'data': data, 'date': datetime.datetime.utcnow().timestamp()})
        print_info("Add trancaction", self._transactions[-1])
        self._save_transactions()
        return True

    def run(self):
        if exists_path(dirs=['data', 'pool'], file='save_data'):
            # Создание генезис блока
            hash_last, genesis_time, self._now_block_number = LoadJsonFile(dirs=['data', 'pool'],
                                                                           file='save_data').as_list()
            self._now_block_number += 1

        else:
            hash_last = '0'
            genesis_time = datetime.datetime.utcnow().timestamp()
            SaveJsonFile(dirs=['data', 'pool'], file='save_data', data=[hash_last, genesis_time, 0])

        while True:
            sleep_sec = genesis_time + (60 * self._now_block_number) - datetime.datetime.utcnow().timestamp()
            if sleep_sec < 0:
                sleep_sec = 0
            time.sleep(sleep_sec)

            members = list(self.server_fn.get_workers()) + get_pools_address()

            hash_last_cut = hash_last[-len(members[0]):]
            nearest = members[0]
            for member in members:
                if (hash_last_cut >= member > nearest) or (hash_last_cut <= member < nearest):
                    nearest = member

            ClientState(nearest).all_balance += AMOUNT

            transactions = self._transactions.copy()
            self._transactions = []
            self._save_transactions()
            for i in range(len(transactions) - 1, -1, -1):
                path = get_path(dirs=['data', 'pool', 'waiting_replicas'],
                                file=transactions[i]['data'])
                sender = transactions[i]['sender']
                size = os.path.getsize(path)
                data_file = LoadJsonFile(dirs=['data', 'pool', 'waiting_replicas'],
                                         file=transactions[i]['data']).as_list()
                if len(data_file) == 3:
                    for hash in data_file[2]:
                        size += get_size_file(dirs=['data', 'pool', 'waiting_replicas'], file=hash)
                client = ClientState(sender)
                if client.all_balance < client.occupied_balance + size:
                    print_error("Transaction ERROR", transactions[i])
                    transactions.pop(i)
                    if len(data_file) == 3:
                        for hash in data_file[2]:
                            os.remove(get_path(dirs=['data', 'pool', 'waiting_replicas'], file=hash))
                    os.remove(path)
                else:
                    print_info("Transaction OK", transactions[i])
                    client.add_object(transactions[i]['data'], size)
                    client.occupied_balance += size

            hash_last = self._save_block({'number': self._now_block_number,
                                          'date': datetime.datetime.utcnow().timestamp(),
                                          'recipient': nearest,
                                          'amount': AMOUNT,
                                          'transactions': transactions,
                                          'hash_last': hash_last})
            SaveJsonFile(dirs=['data', 'pool'],
                           file='save_data',
                           data=[hash_last, genesis_time, self._now_block_number])
            if nearest in list(self.server_fn.get_workers()):
                self.server_fn.request(nearest, 'update_balance',
                                       {'amount': ClientState(nearest).all_balance})
            self._now_block_number += 1

    def get_balance(self, address):
        return ClientState(address).all_balance

    def _save_transactions(self):
        with open(get_path(dirs=['data', 'pool'], file='waiting_transaction'), 'wb') as f:
            pickle.dump(self._transactions, f)

    def _save_block(self, data):
        hash_last = hex(int.from_bytes(sha3_256(bytes(_json.dumps(data),
                                                      'utf-8')).digest(), 'big'))[2:]
        SaveJsonFile(dirs=['data', 'pool', 'waiting_replicas'], file=hash_last, data=data)

        self._save_transactions()
        print_info(f'Create block number: {self._now_block_number} {hash_last} - payment address '
                   f'{data["recipient"]} = {data["amount"]}')
        return hash_last

    def get_occupied(self, address):
        return ClientState(address).occupied_balance

    def get_info_object(self, address, id_object):
        return ClientState(address).info_object(id_object)
