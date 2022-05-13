import random
import requests
from math import sqrt
import os
import time
from _pysha3 import keccak_256 as sha3_256
from threading import Thread
from client_state import ClientState
from dns import DNS
from fog_node import SIZE_REPLICA, COUNT_REPLICAS_IN_FOG_NODE
from fog_nodes_state import FogNodesState
from utils import exists_path, get_path, get_size_file, print_error, print_info, get_hash, sorted_dict, \
    LoadJsonFile, SaveJsonFile, DispatcherSaveFiles, is_ttl_file, load_pools_host, save_pools_host, SyncTime
from variables import POOL_ROOT_EXTERNAL_IP, POOL_PORT
from wallet import Wallet

AMOUNT_PAY_FOG_NODE = 1024 ** 2
AMOUNT_PAY_POOL = int(AMOUNT_PAY_FOG_NODE * 0.1)
COUNT_BLOCK_IN_FILE_BLOCKS = 10_000
LEN_CACHE_BLOCKS = 1000
TIME_TO_LIFE_FILE_IN_WAITING_REPLICAS = 3600  # Время жизни файла в секундах


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
                    time.sleep(0.1)
            time.sleep(1)


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
        self._all_active_pools = {}  # Все активные пулы, предыдущая полная версия всех активных пулов
        self._now_active_pools = {}  # Динамическая загрузка активных пулов со всех активных пулов, изменяемый словарь
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

    def stop(self):
        self.stoping = True
        self._garbage_collector.stop()
        while self._garbage_collector.is_alive():
            time.sleep(0.1)

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
            active_pools = self.all_active_pools()
            if self._wallet_pool.address in active_pools:
                active_pools.pop(self._wallet_pool.address)

            for _, item in active_pools.items():
                if data:
                    with open(path_root, 'rb') as f:
                        requests.post(f'http://{self.select_host(*item["params"][0])}:{item["params"][1]}'
                                      f'/send_replica', data=f.read())
                    if data_file[0] == 'file':
                        with open(path, 'rb') as f:
                            requests.post(f'http://{self.select_host(*item["params"][0])}:{item["params"][1]}'
                                          f'/send_replica', data=f.read())
                try:
                    requests.post(f'http://{self.select_host(*item["params"][0])}:{item["params"][1]}/new_transaction',
                                  json=transaction, timeout=5)
                except:
                    pass

        SaveJsonFile(path='data/pool/waiting_transaction', data=self._transactions)
        return 0, "success"

    def is_ready(self):
        return self._ready

    def is_root_pool(self):
        return self._external_ip == POOL_ROOT_EXTERNAL_IP and self._port_pool == POOL_PORT

    def all_active_pools(self):
        return self._all_active_pools.copy()

    def now_active_pools(self):
        return self._now_active_pools.copy()

    def now_active_fog_nodes(self):
        return self._now_active_fog_nodes

    def get_fog_nodes(self):
        return self._server_fn.get_workers()

    def get_replica_in_fog_node(self, id_fog_node, hash):
        return self._server_fn.request(id_worker=id_fog_node, method='get_replica', json={'hash': hash})

    def get_size_replica_in_fog_node(self, id_fog_node, hash):
        return self._server_fn.request(id_worker=id_fog_node, method='get_size', json={'hash': hash})

    def _get_pools_host_pop_me(self):
        all_pools = load_pools_host()
        if self._wallet_pool.address in all_pools:
            all_pools.pop(self._wallet_pool.address)
        return all_pools

    def register_pool(self):
        all_pools = self._get_pools_host_pop_me()

        for _, item in all_pools.items():
            try:
                requests.post(f'http://{self.select_host(*item[0])}:{item[1]}/register_pool',
                              json=(self._external_ip, self._internal_ip, self._wallet_pool.address,
                                    self._port_pool, self._port_cm_pool, self._port_fn_pool)).json()
            except:
                pass

    def _update_active_pools(self):
        all_pools = load_pools_host()
        address_list = sorted(list(all_pools.keys()), key=lambda A: random.random())

        i = -1
        while not len(address_list) == i + 1:
            i += 1
            address = address_list[i]
            if address == self._wallet_pool.address:
                continue

            if address not in self._now_active_pools or self._now_active_pools[address]['fog_nodes'] == -1:
                try:
                    response = requests.get(f'http://{self.select_host(*all_pools[address][0])}:'
                                            f'{all_pools[address][1]}/get_active_pools_and_count_fog_nodes',
                                            timeout=5).json()
                except:
                    continue

                for key_response, item_response in response.items():
                    if Wallet.check_valid_address(key_response):
                        all_pools[key_response] = item_response['params']

                        if item_response['fog_nodes'] != -1:
                            self._now_active_pools[key_response] = item_response

                        if key_response not in address_list:
                            address_list.append(key_response)

        if "" in self._now_active_pools:
            for key, item in list(all_pools.items()):
                if item[0] == self._now_active_pools[""]['params'][0] and item[1] == \
                        self._now_active_pools[""]['params'][1]:
                    self._now_active_pools[key] = {'params': item, 'fog_nodes': self._now_active_pools[""]['fog_nodes']}
            self._now_active_pools.pop("")

        self._now_active_pools[self._wallet_pool.address] = {'params': ((self._external_ip, self._internal_ip),
                                                                        self._port_pool, self._port_cm_pool,
                                                                        self._port_fn_pool),
                                                             'fog_nodes': len(self._now_active_fog_nodes)}

        for address in list(self._now_active_pools):
            if self._now_active_pools[address]['fog_nodes'] == -1:
                self._now_active_pools.pop(address)

        if "" in all_pools:
            all_pools.pop("")

        save_pools_host(all_pools)
        self._all_active_pools = self._now_active_pools

    def load_state(self):
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
                active_pools = self.all_active_pools()
                for address in sorted(list(active_pools.keys()), key=lambda A: random.random()):
                    hosts, port, _, _ = active_pools[address]['params']
                    try:
                        genesis_time = requests.get(f'http://{self.select_host(*hosts)}:{port}/get_genesis_time').json()
                    except:
                        continue
                    if genesis_time:
                        self._genesis_time = genesis_time
                        return


    @property
    def winner_address_pool(self):
        return self._winner_address_pool

    def winner_pool(self):
        winner_pools = {}
        winner = self._winner_address_pool
        count_active_pools = 0
        while not(winner in winner_pools and winner in winner_pools[winner]):
            active_pools = self.all_active_pools()
            active_pools.pop(self._wallet_pool.address)
            for key in list(active_pools):
                if active_pools[key]['fog_nodes'] == 0:
                    active_pools.pop(key)
            count_active_pools = len(active_pools)

            if self._winner_address_pool:
                winner_pools[self._winner_address_pool] = [self._wallet_pool.address]
                count_active_pools += 1
            pools = list(active_pools)

            if pools:
                while pools:
                    address = random.choice(pools)
                    active_pool = active_pools[address]

                    try:
                        winner = requests.get(f'http://{self.select_host(*active_pool["params"][0])}:'
                                              f'{active_pool["params"][1]}/get_current_winner_pool', timeout=5).json()
                    except:
                        pools.remove(address)
                        count_active_pools -= 1
                        continue
                    if winner and type(winner) == str:
                        winner_pools[winner] = winner_pools.get(winner, []) + [address]
                        pools.remove(address)
                        if len(winner_pools[winner]) > count_active_pools // 2:
                            break
                    else:
                        time.sleep(0.1)
                        print(4444444444444, address, winner)
                        print(4444444444444, address, winner_pools)
                        print(4444444444444, address, pools)
            else:
                break
        try:
            print(555555555555555555555, len(winner_pools[winner]),  count_active_pools, winner)
            print(555555555555555555555, winner_pools[winner])
        except:
            pass
        return winner

    def sync_blockchain(self):
        # Синхронизация с другими пулами
        sync_number_block = int((self.sync_utcnow_timestamp() - self._genesis_time) // 60)
        while True:
            if sync_number_block < self._now_block_number:
                return

            active_pools = self.all_active_pools()
            active_pools.pop(self._wallet_pool.address)
            count_active_pools = len(active_pools)

            if self._winner_address_pool is None:
                self._winner_address_pool = self.winner_pool()

            current_number_block = sync_number_block
            re_sync = False
            blocks = []
            while not re_sync and self._now_block_number <= current_number_block:
                for address in sorted(list(active_pools), key=lambda A: random.random()):
                    if self._winner_address_pool and current_number_block == sync_number_block and \
                            random.randint(0, count_active_pools) <= int(sqrt(count_active_pools)):
                        address = self._winner_address_pool

                    block = None
                    try:
                        block = requests.get(
                            f'http://{self.select_host(*active_pools[address]["params"][0])}:'
                            f'{active_pools[address]["params"][1]}/get_block/{current_number_block}',
                            timeout=5).json()
                    except Exception as e:
                        pass

                    if not (block and type(block) == dict):
                        continue

                    if current_number_block == sync_number_block and self._winner_address_pool:
                        if (block and block['recipient_pool'] != self._winner_address_pool) or \
                                (block is None and address == self._winner_address_pool):
                            re_sync = True
                            break
                        elif not block and address == self._winner_address_pool:
                            try:
                                winner = requests.get(f'http://{self.select_host(*active_pools[address]["params"][0])}:'
                                                      f'{active_pools[address]["params"][1]}/get_current_winner_pool',
                                                      timeout=5).json()
                            except:
                                re_sync = True
                                break

                            if not winner or (winner and winner == self._winner_address_pool):
                                time.sleep(1)
                            else:
                                re_sync = True
                                break

                    if not block or block and len(blocks) > 0 and get_hash(block) != blocks[-1]['hash_last_block']:
                        continue

                    blocks.append(block)
                    current_number_block -= 1
                    break
                if re_sync:
                    self._update_active_pools()
                    break
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

    def _build_new_block(self, winner_address_pool: str, winner_address_fog_node: str, amount:int):
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
        self.register_pool()
        self._update_active_pools()

        # Загружаем и синхранизируем блокчейн
        if not self.is_root_pool():
            self.sync_time()
        self.load_state()

        self._garbage_collector.start()

        print(f'Start POOL {self._wallet_pool.address}')
        self._ready = True
        while True:
            if not self.is_root_pool():
                self.sync_time()
            self.sync_blockchain()
            while self._server_fn.get_count_workers() == 0:
                if self.stoping:
                    return
                time.sleep(1)
                self._winner_address_pool = None
                self.sync_blockchain()

            next_time_block = self._genesis_time + (60 * self._now_block_number)
            print_info("")
            print_info(f'================================ № блока {self._now_block_number} ============ ожидание '
                       f'{int(next_time_block - self.sync_utcnow_timestamp())}сек '
                       f'до запечатывания блока ================================')

            while next_time_block - self.sync_utcnow_timestamp() > 0:
                if self.stoping:
                    return
                time.sleep(0.1)

            self._winner_address_pool = None
            self._now_active_fog_nodes = self.get_fog_nodes()
            for address in self._now_active_pools:
                self._now_active_pools[address]['fog_nodes'] = -1
            time.sleep(5)

            while True:
                if self.stoping:
                    return
                self._update_active_pools()
                all_active_pools = self.all_active_pools()
                active_pools_with_fog_nodes = [key for key, item in all_active_pools.items() if
                                               item['fog_nodes'] != 0]
                print(333333333333, all_active_pools)
                print(222222222222, active_pools_with_fog_nodes)
                ip_active_pools = list(set([all_active_pools[address]["params"][0][0]
                                            for address in all_active_pools]))
                count_ip_active_pools = len(ip_active_pools)

                if active_pools_with_fog_nodes and (count_ip_active_pools > 1 or \
                        (count_ip_active_pools == 1 and ip_active_pools[0] == POOL_ROOT_EXTERNAL_IP)):
                    if not self._ready:
                        self._winner_address_pool = None
                        self._ready = True
                        break
                    # находим пул, который будет запечатывать блок у которого хэш последнего блока ближе
                    # к хэшу активного пула
                    self._winner_address_pool = self._find_min_distance_address(hash=self._hash_last_block,
                                                                                addresses=active_pools_with_fog_nodes)

                    print_info("Active pools")
                    for key, item in all_active_pools.items():
                        print(key, 'fog_nodes:', item['fog_nodes'])
                    print_info()
                    print_info("hash_last_block", self._now_block_number - 1, self._hash_last_block)
                    print_info()
                    print_info('addresses pool', active_pools_with_fog_nodes)
                    print_info('hashes addresses pool',
                               [sha3_256(pool.encode('utf-8')).hexdigest() for pool in active_pools_with_fog_nodes])
                    print_info('Payment address pool', self._winner_address_pool,
                               self._wallet_pool.address == self._winner_address_pool)
                    print_info()
                    print_info('addresses fog_node', self._now_active_fog_nodes)
                    print_info('hashes addresses fog_node',
                               [sha3_256(node.encode('utf-8')).hexdigest() for node in self._now_active_fog_nodes])

                    print(111111111111, self._winner_address_pool)
                    self._winner_address_pool = self.winner_pool()
                    print(222222222222, self._winner_address_pool)
                    if self._winner_address_pool is None:
                        for address in self._now_active_pools:
                            self._now_active_pools[address]['fog_nodes'] = -1
                        continue

                    # если найденный пул - это текущий пул, то запечатываем блок
                    if self._wallet_pool.address == self._winner_address_pool:
                        # находим активную fog_node текущего пула у которого хэш последнего блока ближе к хэшу адреса fog_node
                        winner_address_fog_node = self._find_min_distance_address(hash=self._hash_last_block,
                                                                                  addresses=self._now_active_fog_nodes)

                        print_info('Payment address fog_node', winner_address_fog_node)
                        print_info()

                        count_fog_nodes = sum([item['fog_nodes'] for key, item in all_active_pools.items()])
                        amount = int((count_fog_nodes * COUNT_REPLICAS_IN_FOG_NODE * SIZE_REPLICA) / (60 * 24 * 365))

                        self._build_new_block(self._winner_address_pool, winner_address_fog_node, amount)
                        self._now_block_number += 1
                    break
                else:
                    self._ready = False
                    time.sleep(1)
                    print_info('Нет соединения')

    def _save_block(self, block):
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
            active_pools = self.all_active_pools()
            active_pools.pop(self._wallet_pool.address)

            for transaction in block['transactions']:
                sort_transaction = sorted_dict(transaction)
                hash = get_hash(sort_transaction)

                if transaction['data']:
                    # Получаем root main replica транзакции, если ее нет в waiting_replicas, то догружаем с других пулов
                    while True:
                        main_replica = LoadJsonFile(f'data/pool/waiting_replicas/{transaction["data"]}').as_list()
                        if main_replica:
                            break

                        hosts, port, _, _ = active_pools[random.choice(list(active_pools))]["params"]
                        try:
                            response = requests.get(f'http://{self.select_host(*hosts)}:{port}/load_replica/'
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
            block['hash_block'] = hash_last_block
            all_active_pools_for_app = self.all_active_pools()
            count_all_active_pools, count_all_active_fog_nodes = 0, 0
            for key in all_active_pools_for_app:
                if all_active_pools_for_app[key]['fog_nodes'] > 0:
                    count_all_active_pools += 1
                    count_all_active_fog_nodes += all_active_pools_for_app[key]['fog_nodes']
            for worker in self._server_app.get_workers():
                self._server_app.request(id_worker=worker, method='update_app_pool',
                                         json={'block': block, 'active_pool': count_all_active_pools,
                                               'active_fog_nodes': count_all_active_fog_nodes})
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
        try:
            return LoadJsonFile(f'data/pool/waiting_replicas/{self._blocks.get_hash_block(number_block)}').as_dict()
        except:
            return {}


class BlockchainState:
    def __init__(self, dispatcher):
        self._count_block = LoadJsonFile('data/pool/blocks/state').as_integer()
        self._dispatcher = dispatcher
        self._cache = []

    def add_block(self, hash):
        name_file = f'data/pool/blocks/{self._count_block // COUNT_BLOCK_IN_FILE_BLOCKS}'
        self._dispatcher.add(name_file, LoadJsonFile(name_file).as_list() + [hash])
        self._cache.append((self._count_block, hash))
        self._count_block += 1
        self._dispatcher.add('data/pool/blocks/state', self._count_block)

    def get_hash_block(self, number):
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
