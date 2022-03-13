import requests
from _pysha3 import keccak_256 as sha3_256
import os
import time
from threading import Thread
from dctp import ClientDCTP
from utils import get_pools_host, get_path, exists_path, get_size_file, SaveJsonFile, print_error
from variables import POOL_PORT, POOL_FN_PORT, POOL_ROOT_IP, POOL_CM_PORT
from wallet import Wallet

SIZE_REPLICA = 1024 ** 2
COUNT_REPLICAS_IN_FOG_NODE = 100  # 30 * 1024
COUNT_REPLICAS_IN_CLIENTS_STORAGES = 200
SLICE_FOR_RANDOM_HASH = 10


class BaseFogNode:
    def __init__(self):
        self._size_fog_node = 0
        self._id_fog_node = None
        self._all_hash_replicas = []
        self._main_dir_data = None

    def _save_replica(self, replica, random_replica=False):
        if random_replica:
            hex_hash = sha3_256(replica).hexdigest()[:SLICE_FOR_RANDOM_HASH]
        else:
            hex_hash = sha3_256(replica).hexdigest()

        # находим путь для сохранения разбивая хэш на пары. Создаемм папки и сохраняем файл
        path = f'data/{self._main_dir_data}/{self._id_fog_node}/' \
               f'{"/".join([hex_hash[i:i + 2] for i in range(0, len(hex_hash), 2)])}'

        if not exists_path(path):
            with open(get_path(path), 'wb') as f:
                f.write(replica)
        else:
            pass
            # доработать в будущем проверку, если хэш файла одинаковым, а содержимое файлов разное

        # Добавляет в список self._all_hash_replicas хэши блоков
        self._all_hash_replicas.append(hex_hash)
        self._size_fog_node += get_size_file(path)

        return hex_hash

    def _load_replica(self, hash):
        # Находим файл по хэшу и возвращаем собержимое файла в виде реплики
        path = f'data/{self._main_dir_data}/{self._id_fog_node}/' \
               f'{"/".join([hash[i:i + 2] for i in range(0, len(hash), 2)])}'
        if exists_path(path):
            with open(get_path(path), 'rb') as f:
                data = f.read()
            if hash != sha3_256(data).hexdigest():
                self._delete_replica(hash)
        if not exists_path(path):
            raise Exception('В будущем дописать, если файла нет то делать запрос в pool')
        return data  # Возвращаем бинарный данные файла

    def _delete_replica(self, id_replica):
        # Удаляем файл и пустые папки с названием id_replica
        dirs = [id_replica[i:i + 2] for i in range(0, len(id_replica) - 2, 2)]
        # Удаляем файл с бинарными данными
        os.remove(get_path(f'data/{self._main_dir_data}/{self._id_fog_node}/{"/".join(dirs)}/{id_replica[-2:]}'))
        try:
            # Удаляет пустые папки по пути к файлу
            for i in range(len(dirs), 0, -1):
                path = f'data/{self._main_dir_data}/{self._id_fog_node}/{"/".join(dirs[:i])}/'
                self._size_fog_node -= get_size_file(path)
                os.rmdir(get_path(path))
        except:
            # Если папка не пустая, то срабатывает исключение и папка не удаляется
            pass

    @property
    def id_fog_node(self):
        return self._id_fog_node


class FogNode(BaseFogNode, Thread):
    def __init__(self, process_client, private_key=None):
        BaseFogNode.__init__(self)
        Thread.__init__(self)
        self.pool_ip, self.pool_port = None, None
        if not exists_path('data/fog_nodes/pools_host'):
            SaveJsonFile('data/fog_nodes/pools_host', {})
        self._process_client = process_client
        self._main_dir_data = 'fog_nodes'
        self._pool_client = None

        if private_key is None:
            # Создаем private_key сами
            # и получаем address
            wallet = Wallet()
            wallet.save_private_key('data/fog_nodes/key')
            self._id_fog_node = wallet.address
            self._check_state = 'create'
        else:
            # Получаем address
            wallet = Wallet(private_key)
            self._id_fog_node = wallet.address
            self._check_state = 'load'
        self._wallet = wallet

    @property
    def wallet(self):
        return self._wallet

    def _create_random_init_replica(self):
        # Создаем 1 блок со случайными данными.
        self._save_replica(os.urandom(SIZE_REPLICA), random_replica=True)

    def _load_and_check_replicas(self):
        # Загружаем все данные в Fog Nodes, проверяем их целостность.
        path = get_path(f'data/{self._main_dir_data}/{self._id_fog_node}/')
        for directory_path, directory_names, file_names in os.walk(path):
            for file_name in file_names:
                # Ноходим путь к файлу и сравниваем его с хэшом файла,
                # проверяем в блокчейне существование данного хэша,
                # в противном случаем удалем файл
                hash_replica = ''.join(directory_path[len(path):].split('\\')) + file_name
                file = open(os.path.join(directory_path, file_name), 'rb').read()
                if sha3_256(file).hexdigest()[-len(hash_replica):] == hash_replica and \
                        (len(hash_replica) == SLICE_FOR_RANDOM_HASH or (len(hash_replica) == 64)):
                    self._all_hash_replicas.append(hash_replica)
                    # self._size_fog_node += os.path.getsize(os.path.join(directory_path, file_name))
                else:
                    self._delete_replica(hash_replica)
        # Добавляем рандомные блоки, если какие-то файлы были удалены,
        # чтобы размер плота был = COUNT_REPLICAS_IN_FOG_NODE * SIZE_REPLICA
        while COUNT_REPLICAS_IN_FOG_NODE * SIZE_REPLICA - self._size_fog_node >= SIZE_REPLICA:
            self._create_random_init_replica()

    @property
    def pool_client(self):
        return self._pool_client

    def _get_connect_address_pool(self):
        while True:
            pools = get_pools_host('data/fog_nodes/pools_host')
            if not pools:
                pools[''] = (POOL_ROOT_IP, POOL_PORT, POOL_CM_PORT, POOL_FN_PORT)
            active_pools = {}
            for key, item in list(pools.items()):
                try:
                    response = requests.get(f'http://{item[0]}:{item[1]}/get_active_pools').json()
                    for key_response, item_response in response.items():
                        active_pools[key_response] = item_response
                        pools[key_response] = item_response
                except:
                    pass
            if '' in pools.keys():
                pools.pop('')
            SaveJsonFile('data/fog_nodes/pools_host', pools)

            count_fog_nodes = []
            for key, item in active_pools.items():
                try:
                    count_fog_nodes.append((key, requests.get(
                        f'http://{item[0]}:{item[1]}/get_active_count_fog_nodes').json()))
                except:
                    pass

            if count_fog_nodes:
                count_fog_nodes.sort(key=lambda x: x[1])
                address = count_fog_nodes[0][0]

                min_count_pool_connection = -1
                if self.pool_ip:
                    try:
                        min_count_pool_connection = requests.get(
                            f'http://{self.pool_ip}:{self.pool_port}/get_active_count_fog_nodes').json()
                    except:
                        pass
                if min_count_pool_connection == count_fog_nodes[0][1]:
                    return
                self.min_count_pool_connection = count_fog_nodes[0][1]

                return active_pools[address]

            print_error('Нет соединения с active pools')
            time.sleep(2)

    def _connect_pool(self):
        item = self._get_connect_address_pool()
        if item:
            self.pool_ip, self.pool_port, port_fn = item[0], item[1], item[3]

            pool_client = ClientDCTP(self.wallet.address, self.pool_ip, port_fn)

            @pool_client.method('update_balance')
            def update_balance(data):
                self._process_client.request(self._id_fog_node, 'update_balance_fog_node',
                                             json={'amount': data['amount'], 'id_fog_node': self._id_fog_node})

            pool_client.start()
            if self._pool_client:
                self._pool_client.stop()
            self._pool_client = pool_client

    def run(self):
        self._process_client.request(self._id_fog_node, 'current_state_fog_node',
                                     json={'state': 'connecting', 'id_fog_node': self._id_fog_node})

        self._connect_pool()

        self._process_client.request(self._id_fog_node, 'current_state_fog_node',
                                     json={'state': 'preparing', 'id_fog_node': self._id_fog_node})

        if self._check_state == 'create':
            # Создаем начальные replicas
            print(f'Create FOG NODE {self.wallet.address} in {self._process_client._worker_name}')
            for _ in range(COUNT_REPLICAS_IN_FOG_NODE):
                self._create_random_init_replica()
        elif self._check_state == 'load':
            print(f'Load FOG NODE {self.wallet.address} in {self._process_client._worker_name}')
            self._load_and_check_replicas()

        if self._pool_client.is_alive():
            self._process_client.request(self._id_fog_node, 'update_balance_fog_node',
                                         json=self._pool_client.request(self._id_fog_node, 'get_balance'))
        self._process_client.request(self._id_fog_node, 'current_state_fog_node',
                                     json={'state': 'work', 'id_fog_node': self._id_fog_node})

        while True:
            time.sleep(60)
            self._connect_pool()
