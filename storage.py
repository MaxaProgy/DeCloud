import hashlib
import json
import os
import time
from threading import Thread

from wallet import Wallet

SIZE_REPLICA = 1024 ** 2
COUNT_REPLICAS_IN_STORAGE = 100  # 30 * 1024
COUNT_REPLICAS_IN_CLOUD = 200

SLICE_FOR_RANDOM_HASH = 10


def get_path(directory, id_storage, *args):
    if directory == 'cloud':
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'cloud', id_storage, 'cash', *args)
    elif directory == 'storage':
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'storages', id_storage, *args)


class BaseStorage:
    def __init__(self, private_key=None):
        self._directory = ''
        self._all_hash_replicas = []
        self._size_storage = 0
        if private_key is None:
            # Создаем private_key сами
            # и получаем address
            wallet = Wallet()
            wallet.save_private_key()
            self._id_storage = wallet.address
        else:
            # Получаем address
            wallet = Wallet(private_key)
            self._id_storage = wallet.address

    def _save_replica(self, replica):
        hex_hash = hashlib.sha3_256(replica).hexdigest()[:SLICE_FOR_RANDOM_HASH]
        # находим путь для сохранения разбивая хэш на пары. Создаемм папки и сохраняем файл
        path_to_dir_file = get_path(self._directory, self._id_storage,
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

    def _delete_replica(self, id_replica):
        # Удаляем файл и пустые папки с названием id_replica
        path_to_file = [id_replica[i:i + 2] for i in range(0, len(id_replica) - 2, 2)]
        # Удаляем файл с бинарными данными
        os.remove(get_path(self._directory, self._id_storage,
                           *path_to_file, id_replica[-2:]))
        try:
            # Удаляет пустые папки по пути к файлу
            for i in range(len(path_to_file), 0, -1):
                path = get_path(self._directory,
                                self._id_storage, *path_to_file[:i])
                self._size_storage -= os.path.getsize(path)
                os.rmdir(path)

        except:
            # Если папка не пустая, то срабатывает исключение и папка не удаляется
            pass

    @property
    def id_storage(self):
        return self._id_storage


class FileFS:
    def __init__(self, name, hash):
        self._name = name
        self._hash = hash

    @property
    def name(self):
        return self._name

    @property
    def hash(self):
        return self._hash

    def is_file(self):
        # Проверяем на файл ли это
        return type(self) == FileFS


class DirectoryFS:
    def __init__(self, name, hash, parent):
        self._name = name
        self._hash = hash
        self._children = []
        self._parent = parent

    @property
    def name(self):
        return self._name

    @property
    def hash(self):
        return self._hash

    def get_children(self):
        return self._children

    def add_child(self, child):
        # Добавление вложеных в директорию директорий и папок
        self._children.append(child)

    def is_file(self):
        # Проверяем на файл ли это
        return type(self) == FileFS


class CloudFS(BaseStorage):
    # Файловая система
    def __init__(self, private_key):
        BaseStorage.__init__(self, private_key)
        # Создание корневной - главной директории
        self._root_dir = DirectoryFS(self._id_storage, None, None)
        self._current_dir = self._root_dir

    def make_dir(self, parent, name):
        # Создание папки в файловой системе
        hash = self._save_replica(bytes(json.dumps([parent.hash, name]), 'utf-8'))
        new_dir = DirectoryFS(name, hash, self.current_dir)
        self._current_dir.add_child(new_dir)
        return new_dir

    @property
    def root_dir(self):
        return self._root_dir

    @property
    def current_dir(self):
        return self._current_dir

    def new_file(self, parent, name, data):
        # Создание нового файла в файловой системе
        hashes = [self._save_replica(data[SIZE_REPLICA * count: SIZE_REPLICA * (count + 1)])
                  for count in range(int(len(data) / SIZE_REPLICA) + (len(data) % SIZE_REPLICA > 0))]
        hash_file = self._save_replica(bytes(json.dumps([parent.hash, name, hashes]), 'utf-8'))
        file = FileFS(name, hash_file)
        self._current_dir.add_child(file)

    def change_dir(self, new_dir):
        # Устанавливаем текущую директорию
        self._current_dir = new_dir


class ClientCloud:
    def __init__(self, ip_addr_pool, port=5000, private_key=None):
        self._cloud_fs = CloudFS(private_key)
        self._directory = 'cloud'

        if private_key is None:
            os.mkdir(get_path(self._directory, self._cloud_fs.id_storage, 'cash'))

    def load_from_file(self, file_name):
        # Загрузка данных из файла
        with open(file_name, "rb") as f:
            data = f.read()

        # Добавление файла в файловую систему
        self._cloud_fs.new_file(self._cloud_fs.current_dir, file_name.split('/')[-1], data)
        print(f'Файл {file_name} соханён.')


class Storage(BaseStorage):
    def __init__(self, ip_addr_pool, port=5000, private_key=None):
        BaseStorage.__init__(self, private_key)
        # self._client = ClientDCTP(private_key, type_connection='duplex')
        # self._client.connect(ip_addr_pool, port)
        self._directory = 'storage'
        if private_key is None:
            # Создаем начальные replicas
            for _ in range(COUNT_REPLICAS_IN_STORAGE):
                self._create_random_init_replica()
        else:
            self._load_and_check_replicas()
            # Добавляем рандомные блоки, если какие-то файлы были удалены,
            # чтобы размер плота был = COUNT_REPLICAS_IN_STORAGE * SIZE_REPLICA
            while COUNT_REPLICAS_IN_STORAGE * SIZE_REPLICA - self._size_storage >= SIZE_REPLICA:
                self._create_random_init_replica()

    def _create_random_init_replica(self):
        # Создаем 1 блок со случайными данными.
        self._save_replica(os.urandom(SIZE_REPLICA))

    def _load_and_check_replicas(self):
        # Загружаем все данные в Storage, проверяем их целостность.
        path_storage = get_path(self._directory, self._id_storage)
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
