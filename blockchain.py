from _pysha3 import keccak_256 as sha3_256
import json as _json
import datetime
import os
import time
from threading import Thread

from utils import exists_path, get_path, get_size_file, print_error, \
    print_info, LoadJsonFile, SaveJsonFile, DispatcherSaveFiles, get_pools_host
from variables import POOL_ROOT_IP, POOL_PORT
from wallet import Wallet

AMOUNT = 1024 ** 2


class ClientState:
    def __init__(self, address):
        self._address = address
        self._state_client = {'all_balance': 0,
                              'occupied_balance': 0,
                              'objects': {}}
        self._path = f'data/pool/state/{"/".join([self._address[i:i + 2] for i in range(0, len(self._address), 2)])}'
        self._load_state()

    def _load_state(self):
        if not exists_path(self._path):
            return
        self._state_client = LoadJsonFile(self._path).as_dict()

    def _save_state(self):
        SaveJsonFile(self._path, data=self._state_client)

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
    def __init__(self, parent, server_cm, server_fn):
        super().__init__()
        self._now_block_number = 0  # Номер текущего блока
        self._server_fn = server_fn  # DCTP server для общения с FogNode
        self._server_cm = server_cm
        self.parent = parent
        self._dispatcher_save = DispatcherSaveFiles()

        # Загружаем транзакции, которые ожидают обработки
        self._transactions = LoadJsonFile(path='data/pool/waiting_transaction').as_list()

    def new_transaction(self, sender, owner=None, count=0, data=None):
        # Создание новой транзакции
        if data:  # При наличии контрольной реплики со всеми хешами файла
            path = get_path(path=f'data/pool/waiting_replicas/{data}')
            if not os.path.exists(path):  # Если нет контрольной реплики, то не создаем транзакцию
                print_error('Error Not main replica', data)
                return False
            count = os.path.getsize(path)

            data_file = LoadJsonFile(path=f'data/pool/waiting_replicas/{data}').as_list()
            if len(data_file) == 3:
                for hash in data_file[2]:
                    path = get_path(path=f'data/pool/waiting_replicas/{hash}')
                    if not os.path.exists(path):
                        print_error('Not replica', hash)
                        return False
                    count += os.path.getsize(path)

        self._transactions.append({'sender': sender, 'owner': owner, 'count': count,
                                   'data': data, 'date': datetime.datetime.utcnow().timestamp()})

        print_info("Add trancaction", self._transactions[-1])
        self._dispatcher_save.add(path='data/pool/waiting_transaction', data=self._transactions)
        return True

    def run(self):
        if exists_path(path='data/pool/save_state'):
            hash_last, genesis_time, self._now_block_number = LoadJsonFile(path='data/pool/save_state').as_list()
            self._now_block_number += 1
        else:
            # Создание генезис блока
            hash_last = '0'
            genesis_time = datetime.datetime.utcnow().timestamp()
            self._dispatcher_save.add(path='data/pool/save_state', data=[hash_last, genesis_time, 0])

        while True:
            sleep_sec = genesis_time + (60 * self._now_block_number) - datetime.datetime.utcnow().timestamp()
            if sleep_sec < 0:
                sleep_sec = 0
            time.sleep(sleep_sec)

            # ждем пока появятся активные пулы, ecли пул не мастер-пул
            # или если мастер-пул то в списке пулов не должны быть пулы
            active_pools = list(self.parent.get_active_pools().keys())
            while len(active_pools) == 1 and active_pools[0] == self.parent._wallet.address and \
                    not (self.parent._ip == POOL_ROOT_IP and self.parent._port_pool == POOL_PORT and
                         len(get_pools_host('data/pool/pools_host').keys()) == 0):
                time.sleep(0.1)
                active_pools = list(self.parent.get_active_pools().keys())

            members = list(self._server_fn.get_workers()) + active_pools
            # print(33333333333333333, members)
            hash_last_cut = Wallet.address_build_checksum(hash_last[:len(members[0])])
            # print(members)
            # print_info("hash_last_cut", hash_last_cut)

            nearest = members.pop(0)
            for member in members:
                if nearest < member <= hash_last_cut or \
                        hash_last_cut <= member < nearest or \
                        member < hash_last_cut < nearest:
                    nearest = member
            ClientState(nearest).all_balance += AMOUNT

            transactions = self._transactions.copy()
            self._transactions = []
            self._dispatcher_save.add(path='data/pool/waiting_transaction', data=self._transactions)

            for i in range(len(transactions) - 1, -1, -1):
                path = get_path(path=f'data/pool/waiting_replicas/{transactions[i]["data"]}')
                sender = transactions[i]['sender']
                size = os.path.getsize(path)
                data_file = LoadJsonFile(path=f'data/pool/waiting_replicas/{transactions[i]["data"]}').as_list()
                if len(data_file) == 3:
                    for hash in data_file[2]:
                        size += get_size_file(path=f'data/pool/waiting_replicas/{hash}')
                client = ClientState(sender)
                if client.all_balance < client.occupied_balance + size:
                    print_error("Transaction ERROR", transactions[i])
                    transactions.pop(i)
                    if len(data_file) == 3:
                        for hash in data_file[2]:
                            os.remove(get_path(path=f'data/pool/waiting_replicas/{hash}'))
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
            self._dispatcher_save.add(path='data/pool/save_state',
                                      data=[hash_last, genesis_time, self._now_block_number])
            self._dispatcher_save.commit()
            amount = ClientState(nearest).all_balance
            if nearest in list(self._server_fn.get_workers()):
                self._server_fn.request(nearest, 'update_balance', {'amount': amount})
            else:
                for key in self.parent.active_cm.keys():
                    if nearest in self.parent.active_cm[key]:
                        self._server_cm.request(key, 'update_balance_pool', {'amount': amount, "id_client": nearest})

            print(f'Update balance {nearest} amount={amount}')
            self._now_block_number += 1

    def _save_block(self, data):
        hash_last = hex(int.from_bytes(sha3_256(bytes(_json.dumps(data), 'utf-8')).digest(), 'big'))[2:]
        # Сохраняем блок в папке ожидания
        self._dispatcher_save.add(path=f'data/pool/waiting_replicas/{hash_last}', data=data)
        print_info(f'Create block number: {self._now_block_number} {hash_last} - payment address '
                   f'{data["recipient"]} = {data["amount"]}')
        return hash_last

    @staticmethod
    def get_balance(address):
        return ClientState(address).all_balance

    @staticmethod
    def get_occupied(address):
        return ClientState(address).occupied_balance

    @staticmethod
    def get_info_object(address, id_object):
        return ClientState(address).info_object(id_object)
