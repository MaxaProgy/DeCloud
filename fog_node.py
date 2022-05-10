from random import randrange, random
import requests
from _pysha3 import keccak_256 as sha3_256
import os
from time import sleep
from threading import Thread
from dctp import ClientDCTP
from utils import get_path, exists_path, get_size_file, load_pools_host, save_pools_host, SyncTime
from wallet import Wallet

SIZE_REPLICA = 1024 ** 2
COUNT_REPLICAS_IN_FOG_NODE = 100  # 30 * 1024
COUNT_REPLICAS_IN_CLIENTS_STORAGES = 200
SLICE_FOR_RANDOM_HASH = 10


class BaseFogNode:
    def __init__(self):
        self._size_fog_node = 0
        self._real_size_fog_node = 0
        self._id_fog_node = None
        self._all_hash_replicas = []
        self._main_dir_data = None

    def _save_replica(self, replica, random_replica=False):
        if random_replica:
            hex_hash = sha3_256(replica).hexdigest()[:SLICE_FOR_RANDOM_HASH]
        else:
            if self._size_fog_node + len(replica) > SIZE_REPLICA * COUNT_REPLICAS_IN_FOG_NODE:
                for hash in self._all_hash_replicas:
                    if len(hash) == SLICE_FOR_RANDOM_HASH:
                        self._delete_replica(hash)
                        break
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
        size = get_size_file(path)
        if not random_replica:
            self._all_hash_replicas.append(hex_hash)
            self._real_size_fog_node += size
        self._size_fog_node += size

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
        if exists_path(path):
            return data  # Возвращаем бинарный данные файла

    def _delete_replica(self, id_replica):
        # Удаляем файл и пустые папки с названием id_replica
        dirs = [id_replica[i:i + 2] for i in range(0, len(id_replica) - 2, 2)]
        # Удаляем файл с бинарными данными
        os.remove(get_path(f'data/{self._main_dir_data}/{self._id_fog_node}/{"/".join(dirs)}/{id_replica[-2:]}'))
        try:
            index = self._all_hash_replicas.index(id_replica)
            self._all_hash_replicas.pop(index)
        except ValueError:
            pass

        try:
            # Удаляет пустые папки по пути к файлу
            for i in range(len(dirs), 0, -1):
                path = f'data/{self._main_dir_data}/{self._id_fog_node}/{"/".join(dirs[:i])}/'
                size = get_size_file(path)
                if len(id_replica) != SLICE_FOR_RANDOM_HASH:
                    self._real_size_fog_node -= size
                self._size_fog_node -= size
                os.rmdir(get_path(path))
        except:
            # Если папка не пустая, то срабатывает исключение и папка не удаляется
            pass

    @property
    def id_fog_node(self):
        return self._id_fog_node


class FogNode(BaseFogNode, SyncTime, Thread):
    def __init__(self, process_client, private_key: str):
        BaseFogNode.__init__(self)
        SyncTime.__init__(self)
        Thread.__init__(self)
        self._process_client = process_client
        self._main_dir_data = 'fog_nodes'
        self._pool_client = None
        self._address_pool_now_connect = None
        # Получаем address
        wallet = Wallet(private_key)
        self._id_fog_node = wallet.address
        self._wallet = wallet
        self.stoping = False

    @property
    def wallet(self):
        return self._wallet

    def stop(self):
        self.stoping = True
        if self._pool_client:
            self._pool_client.stop()
            while self._pool_client.is_alive():
                sleep(0.1)

    def _create_random_init_replica(self):
        # Создаем 1 блок со случайными данными.
        self._save_replica(os.urandom(SIZE_REPLICA), random_replica=True)

    def _preparing_replicas(self):
        # Загружаем все данные в Fog Nodes, проверяем их целостность.
        path = get_path(f'data/{self._main_dir_data}/{self._id_fog_node}/')
        for directory_path, directory_names, file_names in os.walk(path):
            for file_name in file_names:
                # Ноходим путь к файлу и сравниваем его с хэшом файла,
                # проверяем в блокчейне существование данного хэша,
                # в противном случаем удалем файл
                hash_replica = ''.join(directory_path[len(path):].split('\\')) + file_name
                file = open(os.path.join(directory_path, file_name), 'rb').read()
                if sha3_256(file).hexdigest()[-len(hash_replica):] == hash_replica:
                    size = os.path.getsize(os.path.join(directory_path, file_name))
                    if len(hash_replica) == SLICE_FOR_RANDOM_HASH:
                        self._size_fog_node += size
                    elif len(hash_replica) == 64:
                        self._all_hash_replicas.append(hash_replica)
                        self._real_size_fog_node += size
                        self._size_fog_node += size
                    else:
                        self._delete_replica(hash_replica)
                else:
                    self._delete_replica(hash_replica)
        # Добавляем рандомные блоки, если какие-то файлы были удалены,
        # чтобы размер плота был = COUNT_REPLICAS_IN_FOG_NODE * SIZE_REPLICA
        while COUNT_REPLICAS_IN_FOG_NODE * SIZE_REPLICA - self._size_fog_node >= SIZE_REPLICA:
            self._create_random_init_replica()

    def _get_connect_address_pool(self):
        while True:
            pools = load_pools_host()
            active_pools = []
            max_fog_nodes = -1
            current_fog_nodes = -1
            if self._pool_client and self._address_pool_now_connect:
                try:
                    current_fog_nodes = requests.get(
                        f'http://{self.select_host(*pools[self._address_pool_now_connect][0])}:'
                        f'{pools[self._address_pool_now_connect][1]}/get_active_count_fog_nodes', timeout=5).json()
                except:
                    pass
                max_fog_nodes = current_fog_nodes

            for key in sorted(list(pools), key=lambda A: random()):
                try:
                    response = requests.get(f'http://{self.select_host(*pools[key][0])}:{pools[key][1]}/'
                                            f'get_active_pools', timeout=5).json()
                except:
                    continue

                for key_response, item_response in response.items():
                    pools[key_response] = item_response
                save_pools_host(pools)

                for key_response in sorted(list(response), key=lambda A: random()):
                    if key_response not in active_pools:
                        try:
                            count_fog_nodes = requests.get(f'http://{self.select_host(*response[key_response][0])}:'
                                                          f'{response[key_response][1]}/get_active_count_fog_nodes',
                                                          timeout=5).json()
                        except:
                            continue
                        active_pools.append(key_response)
                        if max_fog_nodes == -1:
                            max_fog_nodes = count_fog_nodes
                            continue

                        if max_fog_nodes > count_fog_nodes:
                            self._address_pool_now_connect = key_response
                            return pools[key_response]

            if self.stoping:
                return
            elif max_fog_nodes == -1:
                sleep(2)
            elif max_fog_nodes != current_fog_nodes:
                self._address_pool_now_connect = active_pools[-1]
                return pools[active_pools[-1]]
            else:
                return

    def _connect_pool(self):
        new_pool_params = self._get_connect_address_pool()
        if new_pool_params:
            hosts, _, _, port_fn = new_pool_params
            pool_client = ClientDCTP(self.wallet.address, self.select_host(*hosts), port_fn)

            @pool_client.method('update_balance')
            def update_balance(json, data):
                self._process_client.request(id_client=self._id_fog_node, method='update_balance_fog_node',
                                             json={'amount': json['amount'], 'id_fog_node': self._id_fog_node})

            @pool_client.method('get_hash_replicas')
            def get_hash_replicas(json, data):
                return {'hash_replicas': self._all_hash_replicas, 'size_fog_node': self._real_size_fog_node}

            @pool_client.method('save_replica')
            def save_replica(json, data):
                self._save_replica(data)

            @pool_client.method('get_replica')
            def get_replica(json, data):
                return self._load_replica(json['hash'])

            @pool_client.method('get_size')
            def get_size(json, data):
                path = f'data/{self._main_dir_data}/{self._id_fog_node}/' + \
                       '/'.join([json['hash'][i:i + 2] for i in range(0, len(json['hash']), 2)])
                if exists_path(path):
                    return os.path.getsize(get_path(path))

            pool_client.start()

            if self._pool_client:
                self._pool_client.stop()
            self._pool_client = pool_client

    def run(self):
        self._process_client.request(id_client=self._id_fog_node, method='current_state_fog_node',
                                     json={'state': 'connecting', 'id_fog_node': self._id_fog_node})
        self._connect_pool()
        if not self.stoping:
            self._process_client.request(id_client=self._id_fog_node, method='current_state_fog_node',
                                         json={'state': 'preparing', 'id_fog_node': self._id_fog_node})
            self._preparing_replicas()

            try:
                self._process_client.request(id_client=self._id_fog_node, method='update_balance_fog_node',
                                             json=self._pool_client.request('get_balance'))
                self._process_client.request(id_client=self._id_fog_node, method='current_state_fog_node',
                                             json={'state': 'work', 'id_fog_node': self._id_fog_node})
            except:
                pass
        self.sync_time()
        while True:
            date = self.sync_utcnow()
            for _ in range(60 + randrange(10)):
                if self.stoping or not self._pool_client.is_alive():
                    self._address_pool_now_connect = None
                    break
                else:
                    sleep(1)

            if self.stoping:
                break

            if 10 < date.second < 50:
                self._connect_pool()
            else:
                sleep(1)

