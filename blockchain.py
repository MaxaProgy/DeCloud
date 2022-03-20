import random
import requests
from _pysha3 import keccak_256 as sha3_256
import json as _json
import datetime
import os
import time
from threading import Thread
from utils import exists_path, get_path, get_size_file, print_error, \
    print_info, LoadJsonFile, SaveJsonFile, DispatcherSaveFiles, get_pools_host, get_my_ip
from variables import POOL_ROOT_IP, POOL_PORT, POOL_CM_PORT, POOL_FN_PORT
from wallet import Wallet

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
    def __init__(self, parent, server_fn, pool_wallet, _ip_pool, port_pool, port_cm_pool, port_fn_pool):
        super().__init__()
        if not exists_path('data/pool/pools_host'):
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
        self._blocks = {}
        self._all_active_pools = {}
        self._now_active_pools = {}
        self._hash_last_block = "0"
        self._ready = False

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
                if item[0] == self._now_active_pools[""]['params'][0] and item[1] == self._now_active_pools[""]['params'][1]:
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
            self._hash_last_block, self._genesis_time, self._now_block_number = LoadJsonFile('data/pool/save_state').as_list()
            self._blocks = LoadJsonFile('data/pool/blocks').as_dict()
        elif self.is_root_pool():
            # Создание генезис блока
            self._genesis_time = datetime.datetime.utcnow().timestamp()
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
        #print(11111111111111111, (datetime.datetime.utcnow().timestamp() - self._genesis_time) // 60 , self._now_block_number)
        while (datetime.datetime.utcnow().timestamp() - self._genesis_time) // 60 >= self._now_block_number:
            #print(222222222222222, (datetime.datetime.utcnow().timestamp() - self._genesis_time) // 60 , self._now_block_number)
            while self._now_block_number not in self._blocks:
                #print(33333333333333, self._now_block_number, self._blocks)
                active_pools = self.all_active_pools()
                active_pools.pop(self._wallet_pool.address)
                for address in sorted(list(active_pools.keys()), key=lambda A: random.random()):
                    try:
                        block = requests.get(f'http://{active_pools[address]["params"][0]}:'
                                             f'{active_pools[address]["params"][1]}/'
                                             f'get_block/{self._now_block_number}').json()
                        if block:
                            self._hash_last_block = self._save_block(block)
                            self._blocks[self._now_block_number] = self._hash_last_block
                            print_info(f'Load block number: {self._now_block_number} {self._hash_last_block}')
                            break
                    except:
                        pass
                active_pools = self._get_all_active_pools()
                time.sleep(1)
            self._hash_last_block = self._blocks[self._now_block_number]
            self._now_block_number += 1

    @staticmethod
    def _find_min_distance_address(hash:str, addresses:list) -> str:
        min_distance = int('f' * 64, 16)
        for address in addresses:
            distance = abs(int(sha3_256(address.encode('utf-8')).hexdigest(), 16) - int(hash, 16))
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        return nearest_address

    def _build_new_block(self, nearest_address_pool:str, nearest_address_fog_node:str):
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
            print_info(f'Update balance pool {nearest_address_pool} '
                       f'amount={ClientState(nearest_address_pool).all_balance}')

            ClientState(nearest_address_fog_node).all_balance += AMOUNT_PAY_FOG_NODE
            print_info(f'Update balance fog_node {nearest_address_fog_node} '
                       f'amount={ClientState(nearest_address_fog_node).all_balance}')

            self._server_fn.request(nearest_address_fog_node, 'update_balance',
                                    {'amount': ClientState(nearest_address_fog_node).all_balance})

            print_info("")
            #self.send_block_active_pools(block)

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

        print(f'Start POOL {self._wallet_pool.address}')

        if self.is_root_pool() and self._now_block_number == 0:
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
                active_pools_with_fog_nodes = [key for key, item in self.all_active_pools().items() if item['fog_nodes'] != 0]
                if len(active_pools_with_fog_nodes) > 0:
                    break

            print_info("Active pools")
            for key, item in self.all_active_pools().items():
                print(key, 'fog_nodes:', item['fog_nodes'])
            print_info("")
            print_info("hash_last_block", self._now_block_number-1, self._hash_last_block)
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
        hash_last_block = \
            hex(int.from_bytes(sha3_256(bytes(_json.dumps(block, sort_keys=True), 'utf-8')).digest(), 'big'))[2:]

        # Сохраняем блок в папке ожидания
        self._dispatcher_save.add(path=f'data/pool/waiting_replicas/{hash_last_block}', data=block, sort_keys=True)
        self._dispatcher_save.add(path='data/pool/save_state',
                                  data=(hash_last_block, self._genesis_time, block['number']))

        self._blocks[block['number']] = hash_last_block
        self._dispatcher_save.add(path='data/pool/blocks', data=self._blocks)

        self._dispatcher_save.commit()
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
        #if self._now_block_number is None or number_block >= self._now_block_number:
        #    return {}
        try:
            block = LoadJsonFile(f'data/pool/waiting_replicas/{self._blocks[number_block]}').as_dict()
        except:
            return {}
        return block

"""
class BlockchainState:
    def __init__(self, address):
        self._count = -1
        self._pool_address = address

    def save_state(self, hash, number_block):
        while True:
            try:
                with open(str(number_block//10_000), 'a') as f:
                    if number_block - self._count > 1:
                        for i in range(self._count+1, number_block):
                            active_pools = requests.get(f'http://{item[0]}:{item[1]}/get_active_pools').json()
                            if self._pool_address in active_pools:
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

                    f.write(hash)
                    self._count += 1
                    break
            except:
                pass"""