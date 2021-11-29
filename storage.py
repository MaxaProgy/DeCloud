import hashlib
import os
import time
from threading import Thread

from wallet import Wallet

SIZE_REPLICA = 1024 ** 2
COUNT_REPLICAS_IN_STORAGE = 100  # 30 * 1024
COUNT_REPLICAS_IN_CLOUD = 200

SLICE_FOR_RANDOM_HASH = 10


class BaseStorage:
    def __init__(self):
        self._size_storage = 0
        self._id_storage = None
        self._all_hash_replicas = []

    @staticmethod
    def get_path(*args):
        pass

    def _save_replica(self, replica, random_replica=False):
        if random_replica:
            hex_hash = hashlib.sha3_256(replica).hexdigest()[:SLICE_FOR_RANDOM_HASH]
        else:
            hex_hash = hashlib.sha3_256(replica).hexdigest()

        # находим путь для сохранения разбивая хэш на пары. Создаемм папки и сохраняем файл
        path_to_dir_file = self.get_path(self._id_storage,
                                         *[hex_hash[i:i + 2] for i in range(0, len(hex_hash) - 2, 2)])
        path_to_file = os.path.join(path_to_dir_file, hex_hash[-2:])

        if not os.path.exists(path_to_dir_file):
            os.makedirs(path_to_dir_file)
        if not os.path.isfile(path_to_file):
            with open(path_to_file, 'wb') as output:
                output.write(replica)
        else:
            pass
            # доработать в будущем проверку, если хэш файла одинаковым, а содержимое файлов разное

        # Добавляет в список self._all_hash_replicas хэши блоков
        self._all_hash_replicas.append(hex_hash)
        self._size_storage += os.path.getsize(path_to_file)

        return hex_hash

    def _load_replica(self, hash):
        # Находим файл по хэшу и возвращаем собержимое файла в виде реплики
        path_to_dir_file = self.get_path(self._id_storage,
                                         *[hash[i:i + 2] for i in range(0, len(hash) - 2, 2)])
        path_to_file = os.path.join(path_to_dir_file, hash[-2:])
        if os.path.exists(path_to_file):
            with open(path_to_file, 'rb') as f:
                data = f.read()
            if hash != hashlib.sha3_256(data).hexdigest():
                self._delete_replica(hash)
        if not os.path.exists(path_to_file):
            raise Exception('В будущем дописать, если файла нет то делать запрос в pool')
        return data  # Возвращаем бинарный данные файла

    def _delete_replica(self, id_replica):
        # Удаляем файл и пустые папки с названием id_replica
        path_to_file = [id_replica[i:i + 2] for i in range(0, len(id_replica) - 2, 2)]
        # Удаляем файл с бинарными данными
        os.remove(self.get_path(self._id_storage, *path_to_file, id_replica[-2:]))
        try:
            # Удаляет пустые папки по пути к файлу
            for i in range(len(path_to_file), 0, -1):
                path = self.get_path(self._id_storage, *path_to_file[:i])
                self._size_storage -= os.path.getsize(path)
                os.rmdir(path)

        except:
            # Если папка не пустая, то срабатывает исключение и папка не удаляется
            pass

    @property
    def id_storage(self):
        return self._id_storage


class Storage(BaseStorage):
    def __init__(self, ip_addr_pool, port=5000, private_key=None):
        BaseStorage.__init__(self)
        # self._client = ClientDCTP(private_key, type_connection='duplex')
        # self._client.connect(ip_addr_pool, port)

        if private_key is None:
            # Создаем private_key сами
            # и получаем address
            wallet = Wallet()
            wallet.save_private_key_storage()
            self._id_storage = wallet.address
            # Создаем начальные replicas
            for _ in range(COUNT_REPLICAS_IN_STORAGE):
                self._create_random_init_replica()
        else:
            # Получаем address
            wallet = Wallet(private_key)
            self._id_storage = wallet.address
            self._load_and_check_replicas()
            # Добавляем рандомные блоки, если какие-то файлы были удалены,
            # чтобы размер плота был = COUNT_REPLICAS_IN_STORAGE * SIZE_REPLICA
            while COUNT_REPLICAS_IN_STORAGE * SIZE_REPLICA - self._size_storage >= SIZE_REPLICA:
                self._create_random_init_replica()

    @staticmethod
    def get_path(*args):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'storages', *args)

    def _create_random_init_replica(self):
        # Создаем 1 блок со случайными данными.
        self._save_replica(os.urandom(SIZE_REPLICA), random_replica=True)

    def _load_and_check_replicas(self):
        # Загружаем все данные в Storage, проверяем их целостность.
        path_storage = self.get_path(self._id_storage)
        if os.path.exists(path_storage):
            for directory_path, directory_names, file_names in os.walk(path_storage):
                for file_name in file_names:
                    # Ноходим путь к файлу и сравниваем его с хэшом файла,
                    # проверяем в блокчейне существование данного хэша,
                    # в противном случаем удалем файл
                    hash_replica = ''.join(directory_path[len(path_storage) + 1:].split('\\')) + file_name
                    file = open(os.path.join(directory_path, file_name), 'rb').read()
                    if hashlib.sha3_256(file).hexdigest()[-len(hash_replica):] == hash_replica and \
                            (len(hash_replica) == SLICE_FOR_RANDOM_HASH or (len(hash_replica) == 64)):
                        self._all_hash_replicas.append(hash_replica)
                    else:
                        self._delete_replica(hash_replica)

            return {"success": "Ok."}
        else:
            return {'error': f'Directory {self._id_storage} does not exist.'}

    def start(self):
        def worker():
            while True:
                time.sleep(10)

        # run node
        job_node = Thread(target=worker)
        job_node.start()

        print(f'Storage {self._id_storage} готов к работе')
