import asyncio
import json
import random
import aiohttp
import requests
from math import sqrt
import os
from time import sleep
from _pysha3 import keccak_256 as sha3_256
from threading import Thread
from aiohttp import ClientTimeout
from client_state import ClientState
from dns import DNS
from fog_node import SIZE_REPLICA, COUNT_REPLICAS_IN_FOG_NODE
from fog_nodes_state import FogNodesState
from utils import exists_path, get_path, get_size_file, print_error, print_info, get_hash, sorted_dict, \
    LoadJsonFile, SaveJsonFile, DispatcherSaveFiles, is_ttl_file, load_pools_host, save_pools_host, SyncTime
from variables import POOL_ROOT_EXTERNAL_IP, POOL_ROOT_INTERNAL_IP, POOL_PORT
from wallet import Wallet
from datetime import datetime


COUNT_BLOCK_IN_FILE_BLOCKS = 10_000  # количество блоков в одном файле
LEN_CACHE_BLOCKS = 1000  # количество блоков хранимое в памяти
TIME_TO_LIFE_FILE_IN_WAITING_REPLICAS = 3600  # Время жизни файла в папке WAITING_REPLICAS в секундах


class GarbageCollectorWaitingReplicas(Thread):
    def __init__(self, fog_nodes_state, server_fn):
        super().__init__()
        self.stoping = False
        self._fog_nodes_state = fog_nodes_state
        self._server_fn = server_fn

    def stop(self):
        self.stoping = True

    def run(self):
        path = get_path('data/pool/waiting_replicas/')
        while not self.stoping:
            for directory_path, directory_names, file_names in os.walk(path):
                for file_name in file_names:
                    if file_name.find('.tmp') != -1:
                        continue

                    size = get_size_file(path + file_name)
                    fog_nodes_of_free_size = self._fog_nodes_state.get_of_free_size(size)
                    with open(path + file_name, 'rb') as f:
                        data = f.read()

                    is_save_in_replicas = False
                    for fog_node in fog_nodes_of_free_size:
                        if not self._fog_nodes_state.exist_replica(fog_node, file_name):
                            self._server_fn.request(id_worker=fog_node, method='save_replica', data=data)
                            self._fog_nodes_state.add_hash_replica(fog_node, file_name)
                        is_save_in_replicas = True

                    if not self._fog_nodes_state.is_empty and not fog_nodes_of_free_size:
                        # Сделать находжение коэффициента репликации.
                        # Запись в fog nodes, если нет свободного места в подключенных к пулу нодах
                        pass

                    if is_save_in_replicas and not is_ttl_file(directory_path + '\\' + file_name,
                                                               TIME_TO_LIFE_FILE_IN_WAITING_REPLICAS):
                        os.remove(path + '\\' + file_name)
                    sleep(0.1)
            sleep(1)


class Blockchain(SyncTime, Thread):
    def __init__(self, server_fn, server_app, pool_wallet, port_pool, port_cm_pool, port_fn_pool):
        super().__init__()
        self.stoping = False
        self._now_block_number = 0  # Номер текущего блока
        self._server_fn = server_fn  # DCTP server для общения с FogNode
        self._wallet_pool = pool_wallet
        self._port_pool = port_pool
        self._port_cm_pool = port_cm_pool
        self._port_fn_pool = port_fn_pool
        self._server_app = server_app
        self._dispatcher_save = DispatcherSaveFiles()
        self._genesis_time = None
        self._blocks = BlockchainState(self._dispatcher_save)
        # Информация о всех пулах
        self._all_active_pools = {'params': {self._wallet_pool.address: ((self._external_ip, self._internal_ip),
                                                                         self._port_pool, self._port_cm_pool,
                                                                         self._port_fn_pool)},
                                  'fog_nodes': {self._wallet_pool.address: 0}}
        self._now_active_fog_nodes = {}
        self._winner_address_pool = None
        self._hash_last_block = "0"
        self._ready = False  # Готовность блокчейна к работе
        self._transactions = LoadJsonFile(
            'data/pool/waiting_transaction').as_dict()  # Загружаем транзакции, которые ожидают обработки
        self._fog_nodes_state = FogNodesState()
        self._garbage_collector = GarbageCollectorWaitingReplicas(self._fog_nodes_state, self._server_fn)
        self._dns = DNS(self._dispatcher_save)

    def params(self):
        return ((self._external_ip, self._internal_ip),
                self._port_pool, self._port_cm_pool, self._port_fn_pool)

    def get_block_number(self):
        return self._now_block_number

    def stop(self):
        self.stoping = True
        self._garbage_collector.stop()
        while self._garbage_collector.is_alive():
            sleep(0.1)

    def add_fog_node(self, id_fog_node, data):
        self._fog_nodes_state.add(id_fog_node, data)

    def del_fog_node(self, id_fog_node):
        self._fog_nodes_state.delete(id_fog_node)

    def get_exist_replica_in_fog_node(self, id_fog_node, hash):
        return self._fog_nodes_state.exist_replica(id_fog_node, hash)

    def new_transaction(self, sender, date, owner=None, count=0, data=None, is_cm=False):
        # Создание новой транзакции
        if bool(owner) == bool(data):
            # Если нет owner, значит размещение объекта в сети, значит data должана быть
            # Если owner есть, значит перечисление между пользователями, значит data не должна быть,
            return 100, 'Entered parameters "owner" or "data" in transaction is not valid'
        address_normal = self._dns.find_address(sender)
        if address_normal:
            sender = address_normal
        else:
            return 100, f'Parameter "sender" - {sender} is not valid'
        if owner:
            address_normal = self._dns.find_address(owner)
            if address_normal:
                owner = address_normal
            else:
                return 100, f'Parameter "owner" - {owner} is not valid'

        if data and is_cm:  # При наличии контрольной реплики со всеми хешами файла
            if not exists_path(
                    f'data/pool/waiting_replicas/{data}'):  # Если нет контрольной реплики, то не создаем транзакцию
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
            for address in self._all_active_pools['params']:
                if self._wallet_pool.address != address:
                    params = self._all_active_pools['params'][address]
                    if data:
                        with open(path_root, 'rb') as f:
                            requests.post(f'{self._prepare_host(params)}/send_replica', data=f.read())
                        if data_file[0] == 'file':
                            with open(path, 'rb') as f:
                                requests.post(f'{self._prepare_host(params)}/send_replica', data=f.read())
                    try:
                        requests.post(f'{self._prepare_host(params)}/new_transaction', json=transaction, timeout=5)
                    except:
                        pass

        SaveJsonFile(path='data/pool/waiting_transaction', data=self._transactions)
        return 0, "success"

    def is_ready(self):
        return self._ready

    def is_root_pool(self):
        return (self._external_ip, self._internal_ip) == (POOL_ROOT_EXTERNAL_IP, POOL_ROOT_INTERNAL_IP) and \
               self._port_pool == POOL_PORT

    def all_active_pools(self):
        return self._all_active_pools

    def now_active_fog_nodes(self):
        return self._now_active_fog_nodes

    def get_fog_nodes(self):
        return self._server_fn.get_workers()

    def get_count_fog_nodes(self):
        return self._server_fn.get_count_workers()

    def get_replica_in_fog_node(self, id_fog_node, hash):
        return self._server_fn.request(id_worker=id_fog_node, method='get_replica', json={'hash': hash})

    def get_size_replica_in_fog_node(self, id_fog_node, hash):
        return self._server_fn.request(id_worker=id_fog_node, method='get_size', json={'hash': hash}).json

    async def _get_active_pool(self, address_list_queue, all_pools):
        timeout = ClientTimeout(total=None, sock_connect=1, sock_read=5)
        async with aiohttp.ClientSession() as session:
            while not address_list_queue.empty():
                address = await address_list_queue.get()
                if address != self._wallet_pool.address:
                    try:
                        async with session.post(f'http://{self.select_host(*all_pools[address][0])}:'
                                               f'{all_pools[address][1]}/sync_pools',
                                               data=json.dumps((self._wallet_pool.address, ((self._external_ip,
                                                                self._internal_ip), self._port_pool,
                                                                self._port_cm_pool, self._port_fn_pool))),
                                               timeout=timeout) as resp:
                            response = await resp.json()
                    except:
                        if address in self._all_active_pools['params']:
                            self._all_active_pools['params'].pop(address)
                            self._all_active_pools['fog_nodes'].pop(address)
                        continue

                    response_address = response['address']
                    self._all_active_pools['params'][response_address] = response['params'][response_address]
                    self._all_active_pools['fog_nodes'][response_address] = response['fog_nodes']

                    for key_response, item_response in response['params'].items():
                        if Wallet.check_valid_address(key_response):
                            exists = key_response in all_pools
                            all_pools[key_response] = item_response
                            if not exists:
                                await address_list_queue.put(key_response)

    async def _run_update_active_pools(self):
        all_pools = load_pools_host()
        self._all_active_pools['fog_nodes'][self._wallet_pool.address] = self.get_count_fog_nodes()

        address_list_queue = asyncio.Queue()
        [await address_list_queue.put(pool) for pool in all_pools]
        await asyncio.gather(*[asyncio.create_task(self._get_active_pool(address_list_queue, all_pools))
                               for _ in range(500)])
        save_pools_host(all_pools)

    def _update_active_pools(self):
        asyncio.run(self._run_update_active_pools())

    def _load_state(self):
        if exists_path(path='data/pool/save_state'):
            # загружаем state из файла
            self._hash_last_block, self._genesis_time, self._now_block_number = LoadJsonFile(
                'data/pool/save_state').as_list()
        elif self.is_root_pool():
            # Создание генезис блока
            self._genesis_time = self.sync_utcnow_timestamp() // 60 * 60 + 120
        else:
            # загружаем state с любого пула
            while True:
                pools = load_pools_host()
                for address in sorted(list(pools), key=lambda a: random.random()):
                    if address != self._wallet_pool.address:
                        params = pools[address]
                        try:
                            genesis_time = requests.get(f'{self._prepare_host(params)}/genesis_time').json()
                        except:
                            continue
                        if type(genesis_time) == float:
                            self._genesis_time = genesis_time
                            return
                sleep(1)

    @property
    def winner_address_pool(self):
        return self._winner_address_pool

    def winner_pool(self):
        while not self.stoping:
            winner_pools = {}
            address_pools_with_fog_nodes = []
            for address in self._all_active_pools['fog_nodes']:
                if self._all_active_pools['fog_nodes'][address] != 0 and self._wallet_pool.address != address:
                    address_pools_with_fog_nodes.append(address)
            count_active_pools = len(address_pools_with_fog_nodes)

            max_count_winer = 0
            winner = self._winner_address_pool
            if winner:
                winner_pools[winner] = [self._wallet_pool.address]
                count_active_pools += 1
                max_count_winer = 1

            address_winer = winner
            while address_pools_with_fog_nodes:
                address = random.choice(address_pools_with_fog_nodes)
                params = self._all_active_pools['params'][address]

                winner = None
                try:
                    winner = requests.get(f'{self._prepare_host(params)}/get_current_winner_pool', timeout=5).json()
                except:
                    pass

                if type(winner) == str:
                    winner_pools[winner] = winner_pools.get(winner, []) + [address]
                    address_pools_with_fog_nodes.remove(address)
                    if len(winner_pools[winner]) > max_count_winer:
                        max_count_winer = len(winner_pools[winner])
                        address_winer = winner
                elif winner is None:
                    address_pools_with_fog_nodes.remove(address)
                    count_active_pools -= 1

                if max_count_winer > count_active_pools // 2:
                    break
            if address_winer:
                return address_winer
            else:
                self._update_active_pools()

    def _prepare_host(self, params:dict) -> str:
        return f'http://{self.select_host(*params[0])}:{params[1]}'

    def _sync_blockchain(self):
        # Синхронизация блокчейна с другими пулами
        while True:
            sync_number_block = int((self.sync_utcnow_timestamp() - self._genesis_time) // 60)
            count_active_pools = len(self._all_active_pools['params']) - 1
            if sync_number_block < self._now_block_number:
                break

            if self._winner_address_pool is None:
                self._winner_address_pool = self.winner_pool()

            if self._winner_address_pool == self._wallet_pool.address:
                if sync_number_block == self._now_block_number:
                    return
                else:
                    self._winner_address_pool = None
                    continue

            current_number_block = sync_number_block
            blocks = []
            while current_number_block >= self._now_block_number:
                if self.stoping:
                    return
                for address in sorted(list(self._all_active_pools['params']), key=lambda a: random.random()):
                    if self._wallet_pool.address != address:
                        params = self._all_active_pools['params'][address]
                        if current_number_block == sync_number_block and \
                                random.randint(0, count_active_pools) <= int(sqrt(count_active_pools)):
                            address = self._winner_address_pool

                        block = None
                        try:
                            block = requests.get(f'{self._prepare_host(params)}/get_block/{current_number_block}',
                                timeout=5).json()
                        except Exception as e:
                            pass
                        if current_number_block == sync_number_block:
                            if (block and block['recipient_pool'] != self._winner_address_pool) or \
                                    (block is None and address == self._winner_address_pool):
                                return
                            elif block == {} and address == self._winner_address_pool:
                                try:
                                    winner = requests.get(f'{self._prepare_host(params)}/get_current_winner_pool',
                                                          timeout=5).json()
                                except:
                                    return
                                if winner == {} or (winner and winner == self._winner_address_pool):
                                    sleep(1)
                                    continue
                                else:
                                    return
                        elif not block or type(block) != dict or \
                                (len(blocks) > 0 and get_hash(block) != blocks[-1]['hash_last_block']):
                            continue

                        if block:
                            blocks.append(block)
                            current_number_block -= 1
                            break
                else:
                    self._update_active_pools()
            for block in reversed(blocks):
                self._hash_last_block = self._save_block(block)
                print_info(f'Load block number: {block["number"]} {self._hash_last_block}')
                self._now_block_number += 1

            sync_number_block = int((self.sync_utcnow_timestamp() - self._genesis_time) // 60)
            if sync_number_block >= self._now_block_number:
                self._winner_address_pool = None

    @staticmethod
    def _find_min_distance_address(hash: str, addresses: list) -> str:
        min_distance = int('f' * 64, 16)
        for address in addresses:
            distance = abs(int(sha3_256(address.encode('utf-8')).hexdigest(), 16) - int(hash, 16))
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        return nearest_address

    def _build_new_block(self, winner_address_pool: str, winner_address_fog_node: str, amount: int):
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

        block = {'number': self._now_block_number,
                 'date': self.sync_utcnow_timestamp(),
                 'recipient_pool': winner_address_pool,
                 'amount_pool': int(amount * 0.1),
                 'recipient_fog_node': winner_address_fog_node,
                 'amount_fog_node': amount - int(amount * 0.1),
                 'transactions': [item for _, item in transactions.items()],
                 'hash_last_block': self._hash_last_block}
        self._hash_last_block = self._save_block(block)
        print_info(f'Create block number: {self._now_block_number} {self._hash_last_block}')

    def run(self):
        check_print_info_block_number = -1
        self._garbage_collector.start()
        self._load_state()
        self._update_active_pools()

        print_info(f'Start POOL {self._wallet_pool.address}')
        while not self.stoping:
            if not self.is_root_pool():
                self.sync_time()
            self._sync_blockchain()
            self._ready = True

            next_time_block = self._genesis_time + (60 * self._now_block_number)
            if check_print_info_block_number != self._now_block_number:
                check_print_info_block_number = self._now_block_number
                print_info("")
                print_info(f'{datetime.fromtimestamp(self.sync_utcnow_timestamp()).strftime("%Y-%m-%d %H:%M:%S")} '
                           f'============ № блока {self._now_block_number} ============ ожидание '
                           f'{int(next_time_block - self.sync_utcnow_timestamp())}сек до запечатывания блока =========')

            while next_time_block - self.sync_utcnow_timestamp() > 0:
                if self.stoping:
                    return
                sleep(0.1)

            self._winner_address_pool = {}
            while not self.stoping:
                if self.get_count_fog_nodes() == 0:
                    self._winner_address_pool = None
                    break

                self._now_active_fog_nodes = self.get_fog_nodes()
                self._update_active_pools()
                active_pools_with_fog_nodes = [address for address, count in self._all_active_pools['fog_nodes'].items()
                                               if count != 0]
                print_info("Active pools")
                [print_info(address, 'fog_nodes:', count, address == self._wallet_pool.address,
                       self._all_active_pools['params'][address])
                                for address, count in self._all_active_pools['fog_nodes'].items()]
                print_info()

                ip_active_pools = list(set([self._all_active_pools["params"][address][0][0]
                                            for address in active_pools_with_fog_nodes]))
                count_ip_active_pools = len(ip_active_pools)
                if count_ip_active_pools > 1 or (count_ip_active_pools == 1 and self.is_root_pool()):
                    # находим пул, который будет запечатывать блок у которого хэш последнего блока ближе
                    # к хэшу адреса активного пула
                    self._winner_address_pool = self._find_min_distance_address(hash=self._hash_last_block,
                                                                                addresses=active_pools_with_fog_nodes)

                    print_info(111111111111, self._winner_address_pool)
                    self._winner_address_pool = self.winner_pool()
                    print_info(222222222222, self._winner_address_pool)
                    print_info()

                    print_info("hash_last_block", self._now_block_number - 1, self._hash_last_block)
                    print_info('Payment address pool', self._winner_address_pool,
                               self._wallet_pool.address == self._winner_address_pool)

                    # если найденный пул - это текущий пул, то запечатываем блок
                    if self._wallet_pool.address == self._winner_address_pool:
                        # находим активную fog_node текущего пула у которого хэш последнего блока ближе
                        # к хэшу адреса fog_node
                        winner_address_fog_node = self._find_min_distance_address(hash=self._hash_last_block,
                                                                                  addresses=self._now_active_fog_nodes)

                        print_info('Payment address fog_node', winner_address_fog_node)
                        print_info()

                        count_fog_nodes = sum([count for _, count in self._all_active_pools['fog_nodes'].items()])
                        amount = int((count_fog_nodes * COUNT_REPLICAS_IN_FOG_NODE * SIZE_REPLICA) / (60 * 24 * 365))

                        self._build_new_block(self._winner_address_pool, winner_address_fog_node, amount)
                        self._now_block_number += 1
                    break
                else:
                    if self._ready:
                        print_info('Нет соединения')
                        self._ready = False
                        self._winner_address_pool = None
                        break
                    sleep(1)

    def _save_block(self, block:dict):
        hash_last_block = get_hash(block)

        # Сохраняем блок в папке ожидания
        self._dispatcher_save.add(path=f'data/pool/waiting_replicas/{hash_last_block}', data=block, sort_keys=True)
        self._dispatcher_save.add(path='data/pool/save_state',
                                  data=(hash_last_block, self._genesis_time, block['number'] + 1))
        self._blocks.add_block(hash_last_block)
        # обновляем и сохраняем состояние баланса

        ClientState(self, block['recipient_pool']).all_balance += block['amount_pool']
        ClientState(self, block["recipient_fog_node"]).all_balance += block['amount_fog_node']

        if block['transactions']:
            for transaction in block['transactions']:
                sort_transaction = sorted_dict(transaction)
                hash = get_hash(sort_transaction)

                if transaction['data']:
                    # Получаем root main replica транзакции, если ее нет в waiting_replicas, то догружаем с других пулов
                    address_pools = list(self._all_active_pools['params'])
                    address_pools.remove(self._wallet_pool.address)

                    while True:
                        main_replica = LoadJsonFile(f'data/pool/waiting_replicas/{transaction["data"]}').as_list()
                        if main_replica:
                            break

                        params = self._all_active_pools['params'][random.choice(address_pools)]
                        try:
                            response = requests.get(f'{self._prepare_host(params)}/load_replica/'
                                                    f'{transaction["data"]}')
                            if response.status_code == 200:
                                with open(get_path(f'data/pool/waiting_replicas/{transaction["data"]}'), 'wb') as f:
                                    for chunk in response.iter_content(1024):
                                        f.write(chunk)
                        except:
                            pass
                    if transaction["data"] and main_replica[0] == 'ns':
                        self._dns.add_ns(main_replica[1], main_replica[2])

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
        if self._server_app and self._server_app.is_alive():
            count_all_active_pools, count_all_active_fog_nodes = 0, 0
            for address in self._all_active_pools['params']:
                if self._all_active_pools['fog_nodes'][address] > 0:
                    count_all_active_pools += 1
                    count_all_active_fog_nodes += self._all_active_pools['fog_nodes'][address]
            for worker in self._server_app.get_workers():
                self._server_app.request(id_worker=worker, method='update_app_pool',
                                         json={'block': block, 'active_pool': count_all_active_pools,
                                               'active_fog_nodes': count_all_active_fog_nodes})
        return hash_last_block

    def get_balance(self, address:str):
        return ClientState(self, address).all_balance

    def get_occupied(self, address:str):
        return ClientState(self, address).occupied_balance

    def get_info_object(self, address:str, id_object):
        return ClientState(self, address).info_object(id_object)

    def get_genesis_time(self):
        return self._genesis_time

    def get_block(self, number_block:int):
        try:
            return LoadJsonFile(f'data/pool/waiting_replicas/{self._blocks.get_hash_block(number_block)}').as_dict()
        except:
            return {}


class BlockchainState:
    def __init__(self, dispatcher):
        self._count_block = LoadJsonFile('data/pool/blocks/state').as_integer()
        self._dispatcher = dispatcher
        self._cache = []

    def add_block(self, hash:str):
        name_file = f'data/pool/blocks/{self._count_block // COUNT_BLOCK_IN_FILE_BLOCKS}'
        self._dispatcher.add(name_file, LoadJsonFile(name_file).as_list() + [hash])
        self._cache.append((self._count_block, hash))
        self._count_block += 1
        self._dispatcher.add('data/pool/blocks/state', self._count_block)

    def get_hash_block(self, number:str):
        if -1 < number < self._count_block:
            for num, hash in reversed(self._cache):
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
