import random
import requests
import datetime
import os
import time

from _pysha3 import keccak_256 as sha3_256
from threading import Thread
from client_state import ClientState
from dispatcher_save_replicas import DispatcherSaveReplicas
from dns import DNS
from fog_node import SIZE_REPLICA, COUNT_REPLICAS_IN_FOG_NODE
from fog_nodes_state import FogNodesState
from utils import exists_path, get_path, get_size_file, print_error, \
    print_info, LoadJsonFile, SaveJsonFile, DispatcherSaveFiles, get_pools_host, get_hash, sorted_dict
from variables import POOL_ROOT_IP, POOL_PORT
from wallet import Wallet

AMOUNT_PAY_FOG_NODE = 1024 ** 2
AMOUNT_PAY_POOL = int(AMOUNT_PAY_FOG_NODE * 0.1)
COUNT_BLOCK_IN_FILE_BLOCKS = 10_000
LEN_CACHE_BLOCKS = 1000


class Blockchain(Thread):
    def __init__(self, server_fn, pool_wallet, _ip_pool, port_pool, port_cm_pool, port_fn_pool):
        super().__init__()
        if not exists_path('data/pool/pools_host'):
            # Создание по умолчанию файла хостов, известных мне пуллов
            SaveJsonFile('data/pool/pools_host', {})

        self._now_block_number = 0  # Номер текущего блока
        self._server_fn = server_fn  # DCTP server для общения с FogNode
        self._wallet_pool = pool_wallet
        self._ip_pool = _ip_pool
        self._port_pool = port_pool
        self._port_cm_pool = port_cm_pool
        self._port_fn_pool = port_fn_pool
        self._dispatcher_save = DispatcherSaveFiles()
        self._genesis_time = None
        self._blocks = BlockchainState(self._dispatcher_save)
        self._all_active_pools = {}  # Все активные пулы, предыдущая полная версия всех активных пулов
        self._now_active_pools = {}  # Динамическая загрузка активных пулов со всех активных пулов, изменяемый словарь
        self._hash_last_block = "0"
        self._ready = False  # Готовность блокчейна к работе
        self._transactions = LoadJsonFile('data/pool/waiting_transaction').as_dict() # Загружаем транзакции, которые ожидают обработки
        self._fog_nodes_state = FogNodesState()
        self._dsr = DispatcherSaveReplicas(self._fog_nodes_state, self._server_fn)
        self._dns = DNS(self._dispatcher_save)

    def add_fog_node(self, id_fog_node, data):
        self._fog_nodes_state.add(id_fog_node, data)

    def del_fog_node(self, id_fog_node):
        self._fog_nodes_state.delete(id_fog_node)

    def new_transaction(self, sender, date, owner=None, count=0, data=None, is_cm=False):
        # Создание новой транзакции
        if bool(owner) == bool(data):
            # Если нет owner, значит размещение объекта в сети, значит data должана быть
            # Если owner есть, значит перечисление между пользователями, значит data не должна быть,
            return 100, 'Entered parameters "owner" or "data" in transaction is not valid'
        if not Wallet.check_valid_address(sender):
            name = self._dns.find_address(sender)
            if name:
                sender = name
            else:
                return 100, f'Parameter "sender" - {sender} is not valid'
        if owner and not Wallet.check_valid_address(owner):
            name = self._dns.find_address(owner)
            if name:
                owner = name
            else:
                return 100, f'Parameter "owner" - {owner} is not valid'

        if data:
            if data and is_cm:  # При наличии контрольной реплики со всеми хешами файла
                if not exists_path(f'data/pool/waiting_replicas/{data}'):  # Если нет контрольной реплики, то не создаем транзакцию
                    return 100, 'Error no main replica'
                path_root = get_path(f'data/pool/waiting_replicas/{data}')
                count = os.path.getsize(path_root)

                path = None
                data_file = LoadJsonFile(f'data/pool/waiting_replicas/{data}').as_list()
                if data_file[0] == 'file':
                    for hash in data_file[3]:
                        if not exists_path(f'data/pool/waiting_replicas/{hash}'):
                            return 100, f'Not replica - {hash}'
                        path = get_path(f'data/pool/waiting_replicas/{hash}')
                        count += os.path.getsize(path)
                elif data_file[0] == 'ns':
                    if Wallet.check_valid_address(data_file[1]):
                        return 100, f'Error ns name - {data_file[1]} is not valid'

        transaction = {'sender': sender, 'owner': owner, 'count': count, 'data': data, 'date': date}
        transaction = dict(sorted(transaction.items(), key=lambda x: x[0]))
        hash = get_hash(transaction)
        self._transactions[hash] = transaction
        print_info("Add trancaction", self._transactions[hash])

        if is_cm:
            active_pools = self.all_active_pools()
            if self._wallet_pool.address in active_pools:
                active_pools.pop(self._wallet_pool.address)
            for _, item in active_pools.items():
                try:
                    if data:
                        with open(path_root, 'rb') as f:
                            requests.post(f'http://{item["params"][0]}:{item["params"][1]}/send_replica', data=f.read())
                        if data_file[0] == 'file' and path:
                            with open(path, 'rb') as f:
                                requests.post(f'http://{item["params"][0]}:{item["params"][1]}/send_replica', data=f.read())
                    requests.post(f'http://{item["params"][0]}:{item["params"][1]}/new_transaction', json=transaction)
                except:
                    pass

        SaveJsonFile(path='data/pool/waiting_transaction', data=self._transactions)
        return 0, "success"

    def is_ready(self):
        return self._ready

    def is_root_pool(self):
        return self._ip_pool == POOL_ROOT_IP and self._port_pool == POOL_PORT

    def all_active_pools(self):
        return self._all_active_pools.copy()

    def now_active_pools(self):
        return self._now_active_pools

    def get_count_fog_nodes(self):
        return self._server_fn.get_count_workers()

    def get_fog_nodes(self):
        return self._server_fn.get_workers()

    def register_pool(self):
        all_pools = get_pools_host('data/pool/pools_host')
        for _, item in all_pools.items():
            try:
                requests.post(f'http://{item[0]}:{item[1]}/register_pool',
                              json=(self._wallet_pool.address, self._port_pool,
                                    self._port_cm_pool, self._port_fn_pool)).json()
            except:
                pass

    def _get_all_active_pools(self):
        self._now_active_pools = {}
        all_pools = get_pools_host('data/pool/pools_host')

        for address in sorted(list(all_pools.keys()), key=lambda A: random.random()):
            if address not in self._now_active_pools:
                try:
                    response = requests.get(f'http://{all_pools[address][0]}:{all_pools[address][1]}/'
                                            f'get_active_pools_and_count_fog_nodes').json()
                    for key_response, item_response in response.items():
                        if Wallet.check_valid_address(key_response):
                            all_pools[key_response] = item_response['params']
                            self._now_active_pools[key_response] = item_response
                except:
                    pass

        if "" in self._now_active_pools:
            for key, item in list(all_pools.items()):
                if item[0] == self._now_active_pools[""]['params'][0] and item[1] == \
                        self._now_active_pools[""]['params'][1]:
                    self._now_active_pools[key] = {'params': item, 'fog_nodes': self._now_active_pools[""]['fog_nodes']}
            self._now_active_pools.pop("")
        self._now_active_pools[self._wallet_pool.address] = {'params': (self._ip_pool, self._port_pool,
                                                                        self._port_cm_pool, self._port_fn_pool),
                                                             'fog_nodes': self.get_count_fog_nodes()}
        if "" in all_pools:
            all_pools.pop("")
        if self._wallet_pool.address in all_pools:
            all_pools.pop(self._wallet_pool.address)
        SaveJsonFile('data/pool/pools_host', all_pools)
        return self._now_active_pools.copy()

    def load_state(self):
        if exists_path(path='data/pool/save_state'):
            # загружаем state из файла
            self._hash_last_block, self._genesis_time, self._now_block_number = LoadJsonFile(
                'data/pool/save_state').as_list()
        elif self.is_root_pool():
            # Создание генезис блока
            self._genesis_time = datetime.datetime.utcnow().timestamp() // 60 * 60
        else:
            # загружаем state с любого пула
            active_pools = self.all_active_pools()
            while True:
                for address in sorted(list(active_pools.keys()), key=lambda A: random.random()):
                    try:
                        ip, port, _, _ = active_pools[address]['params']
                        genesis_time = requests.get(f'http://{ip}:{port}/get_genesis_time').json()
                        if genesis_time:
                            self._genesis_time = genesis_time
                            return
                    except:
                        pass
                active_pools = self._get_all_active_pools()
                time.sleep(1)

    def sync_blockchain(self):
        # Синхронизация с другими пулами
        while (datetime.datetime.utcnow().timestamp() - self._genesis_time) // 60 >= self._now_block_number:
            while self._now_block_number >= len(self._blocks):
                active_pools = self.all_active_pools()
                active_pools.pop(self._wallet_pool.address)
                for address in sorted(list(active_pools.keys()), key=lambda A: random.random()):
                    try:
                        block = requests.get(f'http://{active_pools[address]["params"][0]}:'
                                             f'{active_pools[address]["params"][1]}/'
                                             f'get_block/{self._now_block_number}').json()
                        if block:
                            self._hash_last_block = self._save_block(block)
                            print_info(f'Load block number: {self._now_block_number} {self._hash_last_block}')
                            break
                    except:
                        pass
                active_pools = self._get_all_active_pools()
                time.sleep(1)
            self._hash_last_block = self._blocks.get_hash_block(self._now_block_number)
            self._now_block_number += 1

    @staticmethod
    def _find_min_distance_address(hash: str, addresses: list) -> str:
        min_distance = int('f' * 64, 16)
        for address in addresses:
            distance = abs(int(sha3_256(address.encode('utf-8')).hexdigest(), 16) - int(hash, 16))
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        return nearest_address

    def _build_new_block(self, nearest_address_pool: str, nearest_address_fog_node: str):
        transactions = self._transactions.copy()
        self._transactions = {}
        self._dispatcher_save.add(path='data/pool/waiting_transaction', data=self._transactions)
        for key in list(transactions):
            sender = transactions[key]['sender']
            client = ClientState(self, sender)
            if transactions[key]["data"]:
                path = get_path(f'data/pool/waiting_replicas/{transactions[key]["data"]}')
                data_file = LoadJsonFile(f'data/pool/waiting_replicas/{transactions[key]["data"]}').as_list()

            if transactions[key]['owner'] or data_file[0] == 'ns':
                if client.all_balance - client.occupied_balance - transactions[key]['count'] < 0:
                    print_error("Transaction ERROR. Не хватает бабок", transactions[key])
                    transactions.pop(key)
                    continue
            else:
                size = os.path.getsize(path)
                if data_file[0] == 'file' and len(data_file[3]) != 0:
                    size = size + (len(data_file[3]) - 1) * SIZE_REPLICA + \
                           get_size_file(f'data/pool/waiting_replicas/{data_file[3][-1]}')
                transactions[key]['count'] = size

                if client.all_balance < client.occupied_balance + size:
                    print_error("Transaction ERROR", transactions[key])
                    transactions.pop(key)
                else:
                    print_info("Transaction OK", transactions[key])

            if transactions[key]["data"] and data_file[0] == 'ns':
                self._dns.add_ns(data_file[1], data_file[2])

        count_fog_nodes = sum([item['fog_nodes'] for key, item in self.all_active_pools().items()])
        amount = int((count_fog_nodes * COUNT_REPLICAS_IN_FOG_NODE * SIZE_REPLICA) / (60 * 24 * 365))
        block = {'number': self._now_block_number,
                 'date': datetime.datetime.utcnow().timestamp(),
                 'recipient_pool': nearest_address_pool,
                 'amount_pool': int(amount * 0.1),
                 'recipient_fog_node': nearest_address_fog_node,
                 'amount_fog_node': amount - int(amount * 0.1),
                 'transactions': [item for _, item in transactions.items()],
                 'hash_last_block': self._hash_last_block}
        self._hash_last_block = self._save_block(block)
        print_info(f'Create block number: {self._now_block_number} {self._hash_last_block}')

        print_info("")

    def run(self):
        nearest_address_pool = None
        self.register_pool()
        self._all_active_pools = self._get_all_active_pools()

        # Загружаем и синхранизируем блокчейн
        self.load_state()
        if not self.is_root_pool() or self._now_block_number != 0:
            self.sync_blockchain()

        self._ready = True
        # Ждем пока текущем пуле появятся fog_nodes
        while True:
            if self.get_count_fog_nodes() != 0:
                break
            time.sleep(5)

        self._dsr.start()

        print(f'Start POOL {self._wallet_pool.address}')

        if self.is_root_pool() and self._now_block_number == 0:
            self._all_active_pools = self._get_all_active_pools()
            print_info(f'================================ № блока {self._now_block_number} '
                       f'===================================================================================')
            self._build_new_block(self._wallet_pool.address, self._wallet_pool.address)
            self._now_block_number += 1

        while True:
            self.sync_blockchain()

            next_time_block = self._genesis_time + (60 * self._now_block_number)
            print_info(f'================================ № блока {self._now_block_number} ============ ожидание '
                       f'{int(next_time_block - datetime.datetime.utcnow().timestamp())}сек '
                       f'до запечатывания блока ================================')

            while next_time_block - datetime.datetime.utcnow().timestamp() > 0:
                time.sleep(0.1)

            while True:
                self._now_active_pools = {}
                time.sleep(1)
                self._all_active_pools = self._get_all_active_pools()
                active_pools_with_fog_nodes = [key for key, item in self.all_active_pools().items() if
                                               item['fog_nodes'] != 0]
                if len(active_pools_with_fog_nodes) > 0:
                    break

            print_info("Active pools")
            for key, item in self.all_active_pools().items():
                print(key, 'fog_nodes:', item['fog_nodes'])
            print_info("")
            print_info("hash_last_block", self._now_block_number - 1, self._hash_last_block)
            # находим пул, который будет запечатывать блок у которого хэш последнего блока ближе к хэшу активного пула
            nearest_address_pool = self._find_min_distance_address(hash=self._hash_last_block,
                                                                   addresses=active_pools_with_fog_nodes)
            pool_fog_nodes = self.get_fog_nodes()
            print_info()
            print_info('addresses pool', active_pools_with_fog_nodes)
            print_info('hashes addresses pool',
                       [sha3_256(pool.encode('utf-8')).hexdigest() for pool in active_pools_with_fog_nodes])
            print_info('Payment address pool', nearest_address_pool, self._wallet_pool.address == nearest_address_pool)
            print_info()
            print_info('addresses fog_node', pool_fog_nodes)
            print_info('hashes addresses fog_node',
                       [sha3_256(node.encode('utf-8')).hexdigest() for node in pool_fog_nodes])

            # если найденный пул - это текущий пул, то запечатываем блок
            if self._wallet_pool.address == nearest_address_pool:
                # находим активную fog_node текущего пула у которого хэш последнего блока ближе к хэшу адреса fog_node

                nearest_address_fog_node = self._find_min_distance_address(hash=self._hash_last_block,
                                                                           addresses=pool_fog_nodes)

                print_info('Payment address fog_node', nearest_address_fog_node)
                print_info()

                self._build_new_block(nearest_address_pool, nearest_address_fog_node)
                self._now_block_number += 1

    """
    def send_block_active_pools(self, block):
        active_pools = self.active_pools
        if self._wallet_pool.address in active_pools:
            active_pools.pop(self._wallet_pool.address)

        for address, item in active_pools.items():
            try:
                requests.post(f'http://{item["params"][0]}:{item["params"][1]}/send_new_block', json=block)
            except:
                pass
    
    def update_new_block(self, block):
        hash_last_block = self._save_block(block)
        print_info(f'Update new block number: {block["number"]} {hash_last_block}')
    """

    def _save_block(self, block):
        hash_last_block = get_hash(block)

        # Сохраняем блок в папке ожидания
        self._dispatcher_save.add(path=f'data/pool/waiting_replicas/{hash_last_block}', data=block, sort_keys=True)
        self._dispatcher_save.add(path='data/pool/save_state',
                                  data=(hash_last_block, self._genesis_time, block['number']))

        self._blocks.add_last_block(hash_last_block)

        # обновляем и сохраняем состояние баланса
        ClientState(self, block['recipient_pool']).all_balance += block['amount_pool']
        ClientState(self, block["recipient_fog_node"]).all_balance += block['amount_fog_node']

        for transaction in block['transactions']:
            sort_transaction = sorted_dict(transaction)
            hash = get_hash(sort_transaction)
            if hash in self._transactions:
                self._transactions.pop(hash)
            if transaction['data']:
                client = ClientState(self, transaction["sender"])
                client.add_object(transaction['data'], transaction['count'])
                client.occupied_balance += transaction['count']
            else:
                ClientState(self, transaction["sender"]).all_balance -= transaction['count']
            if transaction['owner']:
                ClientState(self, transaction["owner"]).all_balance += transaction['count']


        self._dispatcher_save.commit()
        return hash_last_block

    def get_balance(self, address):
        return ClientState(self, address).all_balance

    def get_occupied(self, address):
        return ClientState(self, address).occupied_balance

    def get_info_object(self, address, id_object):
        return ClientState(self, address).info_object(id_object)

    def get_genesis_time(self):
        return self._genesis_time

    def get_block(self, number_block):
        # print(1111111111111111, number_block, self._now_block_number)
        # if self._now_block_number is None or number_block >= self._now_block_number:
        #    return {}
        try:
            block = LoadJsonFile(f'data/pool/waiting_replicas/{self._blocks.get_hash_block(number_block)}').as_dict()
        except:
            return {}
        return block


class BlockchainState:
    def __init__(self, dispatcher):
        self._count_block = LoadJsonFile('data/pool/blocks/state').as_integer()
        self._dispatcher = dispatcher
        self._cache = []

    def add_last_block(self, hash):
        name_file = f'data/pool/blocks/{self._count_block // COUNT_BLOCK_IN_FILE_BLOCKS}'
        self._dispatcher.add(name_file, LoadJsonFile(name_file).as_list() + [hash])
        self._count_block += 1
        self._dispatcher.add('data/pool/blocks/state', self._count_block)

    def get_hash_block(self, number):
        if -1 < number < self._count_block:
            for num, hash in self._cache:
                if num == number:
                    return hash

            self._cache.append((number, LoadJsonFile(f'data/pool/blocks/{number // COUNT_BLOCK_IN_FILE_BLOCKS}')
                                .as_list()[number % COUNT_BLOCK_IN_FILE_BLOCKS]))

            if len(self._cache) > LEN_CACHE_BLOCKS:
                self._cache.pop(0)
            return self._cache[-1][1]
        else:
            raise Exception(f'Not number {number} in blocks')

    def __len__(self):
        return self._count_block
