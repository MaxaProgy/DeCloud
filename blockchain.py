import random
import requests
from _pysha3 import keccak_256 as sha3_256
import json as _json
import datetime
import os
import time
from threading import Thread
from utils import exists_path, get_path, get_size_file, print_error, \
    print_info, LoadJsonFile, SaveJsonFile, DispatcherSaveFiles, get_pools_host
from variables import POOL_ROOT_IP, POOL_PORT

AMOUNT_PAY_FOG_NODE = 1024 ** 2
AMOUNT_PAY_POOL = int(AMOUNT_PAY_FOG_NODE * 0.1)


class ClientState:
    def __init__(self, address):
        self._address = address
        self._state_client = {'all_balance': 0, 'occupied_balance': 0, 'objects': {}}
        self._path = f'data/pool/state/{"/".join([self._address[i:i + 2] for i in range(0, len(self._address), 2)])}'
        self._load_state()

    def _load_state(self):
        if not exists_path(self._path):
            return
        self._state_client = LoadJsonFile(self._path).as_dict()

    def _save_state(self):
        SaveJsonFile(path=self._path, data=self._state_client)

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
    def __init__(self, parent, server_fn):
        super().__init__()
        self._now_block_number = None  # Номер текущего блока
        self._server_fn = server_fn  # DCTP server для общения с FogNode
        self.parent = parent
        self._wallet_pool = parent._wallet
        self._dispatcher_save = DispatcherSaveFiles()
        self._genesis_time = None
        self._blocks = {}

        # Загружаем транзакции, которые ожидают обработки
        self._transactions = LoadJsonFile('data/pool/waiting_transaction').as_list()

    def new_transaction(self, sender, owner=None, count=0, data=None):
        # Создание новой транзакции
        if data:  # При наличии контрольной реплики со всеми хешами файла
            path = get_path(f'data/pool/waiting_replicas/{data}')
            if not os.path.exists(path):  # Если нет контрольной реплики, то не создаем транзакцию
                print_error('Error Not main replica', data)
                return False
            count = os.path.getsize(path)

            data_file = LoadJsonFile(f'data/pool/waiting_replicas/{data}').as_list()
            if len(data_file) == 3:
                for hash in data_file[2]:
                    path = get_path(f'data/pool/waiting_replicas/{hash}')
                    if not os.path.exists(path):
                        print_error('Not replica', hash)
                        return False
                    count += os.path.getsize(path)

        self._transactions.append({'sender': sender, 'owner': owner, 'count': count,
                                   'data': data, 'date': datetime.datetime.utcnow().timestamp()})

        print_info("Add trancaction", self._transactions[-1])
        self._dispatcher_save.add(path='data/pool/waiting_transaction', data=self._transactions)
        return True

    @staticmethod
    def _find_min_distance_address(hash, addresses):
        min_distance = int('f' * 64, 16)
        for address in addresses:
            distance = abs(int(sha3_256(address.encode('utf-8')).hexdigest(), 16) - int(hash, 16))
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        return nearest_address

    def _get_active_pools_with_fog_nodes(self):
        # ждем пока появятся активные пулы, ecли пул не мастер-пул
        # или если мастер-пул то в списке пулов не должны быть пулы
        active_pools = None
        while not active_pools or (len(active_pools) == 1 and active_pools[0] == self.parent._wallet.address and \
                                   not (self.parent.is_root_pool and len(get_pools_host('data/pool/pools_host')) == 0)):

            active_pools = self.parent.get_active_pools()
            for address in list(active_pools.keys()):
                try:
                    if requests.get(f'http://{active_pools[address][0]}:{active_pools[address][1]}/'
                                    f'get_active_count_fog_nodes').json() == 0:
                        active_pools.pop(address)
                except:
                    active_pools.pop(address)
            active_pools = list(active_pools.keys())

            if len(active_pools) == 1 and active_pools[0] == self.parent._wallet.address \
                    and self.parent.is_root_pool and len(get_pools_host('data/pool/pools_host')) > 0:
                time.sleep(1)

        return active_pools

    def _get_active_pools(self):
        return self.parent.get_active_pools()

    def sync_state(self):
        if exists_path(path='data/pool/save_state'):
            # загружаем state из файла
            hash_last_block, genesis_time, now_block_number = LoadJsonFile('data/pool/save_state').as_list()
        elif self.parent._ip == POOL_ROOT_IP and self.parent._port_pool == POOL_PORT:
            # Создание генезис блока
            return '0', datetime.datetime.utcnow().timestamp(), 0
        else:
            # загружаем state с любого пула

            now_block_number = 0
            while True:
                try:
                    active_pools = self._get_active_pools()
                    if self.parent._wallet.address in active_pools:
                        active_pools.pop(self.parent._wallet.address)
                    ip, port, _, _ = active_pools[random.choice(list(active_pools.keys()))]
                    genesis_time = requests.get(f'http://{ip}:{port}/get_genesis_time').json()
                    if genesis_time:
                        break
                except:
                    pass
                time.sleep(1)

        # Синхронизация с другими пулами
        block, hash_last_block = None, None
        while True:
            active_pools = self._get_active_pools()
            if self.parent._wallet.address in active_pools:
                active_pools.pop(self.parent._wallet.address)

            if len(active_pools) == 0:
                time.sleep(0.1)
                continue

            for address, item in self._get_active_pools().items():
                try:
                    block = requests.get(f'http://{item[0]}:{item[1]}/get_block/{now_block_number}').json()
                    if block:
                        hash_last_block = self._save_block(block)
                        self._blocks[now_block_number] = hash_last_block
                        print_info(f'Load block number: {now_block_number} {hash_last_block}')
                        now_block_number += 1
                        break
                except:
                    pass

            if not block:
                return hash_last_block, genesis_time, now_block_number

    def run(self):
        nearest_address_pool = None

        # Загружаем и синхранизируем блокчейн
        self._hash_last_block, self._genesis_time, self._now_block_number = self.sync_state()
        while True:
            next_time_block = self._genesis_time + (60 * self._now_block_number)
            print_info(f'================================ № блока {self._now_block_number} ============ ожидание '
                       f'{int(next_time_block - datetime.datetime.utcnow().timestamp())}сек '
                       f'до запечатывания блока ================================')
            while next_time_block - datetime.datetime.utcnow().timestamp() > 0:
                time.sleep(0.1)

            active_pools = self._get_active_pools_with_fog_nodes()

            # находим пул, который будет запечатывать блок у которого хэш последнего блока ближе к хэшу активного пула
            nearest_address_pool = self._find_min_distance_address(hash=self._hash_last_block, addresses=active_pools)

            # если найденный пул - это текущий пул, то запечатываем блок
            if self._wallet_pool.address == nearest_address_pool:
                # находим активную fog_node текущего пула у которого хэш последнего блока ближе к хэшу адреса fog_node
                pool_fog_nodes = self._server_fn.get_workers()
                nearest_address_fog_node = self._find_min_distance_address(hash=self._hash_last_block,
                                                                           addresses=pool_fog_nodes)
                print_info("")
                print_info("hash_last_block", self._hash_last_block)

                print_info("")
                print_info('addresses pool', active_pools)
                print_info('hashes addresses pool',
                           [sha3_256(pool.encode('utf-8')).hexdigest() for pool in active_pools])
                print_info('Payment address pool', nearest_address_pool)
                print_info("")

                print_info('addresses fog_node', pool_fog_nodes)
                print_info('hashes addresses fog_node',
                           [sha3_256(node.encode('utf-8')).hexdigest() for node in pool_fog_nodes])
                print_info('Payment address fog_node', nearest_address_fog_node)
                print_info("")

                transactions = self._transactions.copy()
                self._transactions = []
                self._dispatcher_save.add(path='data/pool/waiting_transaction', data=self._transactions)

                for i in range(len(transactions) - 1, -1, -1):
                    path = get_path(f'data/pool/waiting_replicas/{transactions[i]["data"]}')
                    sender = transactions[i]['sender']
                    size = os.path.getsize(path)
                    data_file = LoadJsonFile(f'data/pool/waiting_replicas/{transactions[i]["data"]}').as_list()
                    if len(data_file) == 3:
                        for hash in data_file[2]:
                            size += get_size_file(f'data/pool/waiting_replicas/{hash}')
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

                block = {'number': self._now_block_number,
                         'date': datetime.datetime.utcnow().timestamp(),
                         'recipient_pool': nearest_address_pool,
                         'amount_pool': AMOUNT_PAY_POOL,
                         'recipient_fog_node': nearest_address_fog_node,
                         'amount_fog_node': AMOUNT_PAY_FOG_NODE,
                         'transactions': transactions,
                         'hash_last_block': self._hash_last_block}
                self._hash_last_block = self._save_block(block)
                print_info(f'Create block number: {self._now_block_number} {self._hash_last_block}')

                # обновляем и сохраняем состояние баланса
                ClientState(nearest_address_pool).all_balance += AMOUNT_PAY_POOL
                ClientState(nearest_address_fog_node).all_balance += AMOUNT_PAY_FOG_NODE

                self._server_fn.request(nearest_address_fog_node, 'update_balance',
                                        {'amount': ClientState(nearest_address_fog_node).all_balance})

                print_info(f'Update balance pool {nearest_address_pool} '
                           f'amount={ClientState(nearest_address_pool).all_balance}')
                print_info(f'Update balance fog_node {nearest_address_fog_node} '
                           f'amount={ClientState(nearest_address_fog_node).all_balance}')
                print_info("")
                self.send_block_active_pools(block)
            self._now_block_number += 1

    def send_block_active_pools(self, block):
        active_pools = self._get_active_pools()
        if self.parent._wallet.address in active_pools:
            active_pools.pop(self.parent._wallet.address)

        for address, item in active_pools.items():
            try:
                requests.post(f'http://{item[0]}:{item[1]}/send_new_block', json=block)
            except:
                pass

    def update_new_block(self, block):
        self._hash_last_block = self._save_block(block)
        print_info(f'Load block number: {block["number"]} {self._hash_last_block}')

    def _save_block(self, block):
        hash_last_block = \
            hex(int.from_bytes(sha3_256(bytes(_json.dumps(block, sort_keys=True), 'utf-8')).digest(), 'big'))[2:]

        # Сохраняем блок в папке ожидания
        self._dispatcher_save.add(path=f'data/pool/waiting_replicas/{hash_last_block}', data=block)
        self._dispatcher_save.add(path='data/pool/save_state',
                                  data=(hash_last_block, self._genesis_time, block['number']))
        self._dispatcher_save.commit()

        self._blocks[block['number']] = hash_last_block
        return hash_last_block

    @staticmethod
    def get_balance(address):
        return ClientState(address).all_balance

    @staticmethod
    def get_occupied(address):
        return ClientState(address).occupied_balance

    @staticmethod
    def get_info_object(address, id_object):
        return ClientState(address).info_object(id_object)

    def get_genesis_time(self):
        return self._genesis_time

    def get_block(self, number_block):
        #print(1111111111111111, number_block, self._now_block_number)
        if self._now_block_number is None or number_block >= self._now_block_number:
            return {}
        return LoadJsonFile(f'data/pool/waiting_replicas/{self._blocks[number_block]}').as_dict()
