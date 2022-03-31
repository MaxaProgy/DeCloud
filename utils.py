import datetime
import os
import json
import time
from shutil import copyfile
from _pysha3 import keccak_256 as sha3_256
from variables import POOL_PORT, POOL_ROOT_IP, POOL_FN_PORT, POOL_CM_PORT
from string import ascii_lowercase
from random import choice

ERROR_VIEW = True
INFO_VIEW = True
WARNING_VIEW = True
TIME_TO_LIFE_FILE = 3600  # Время жизни файла в секундах

_LETTERS = ascii_lowercase
NAME_AMOUNT_FORMAT = ['bEx', 'KbEx', 'MbEx', 'GbEx', 'TbEx', 'PbEx', 'EbEx', 'ZbEx', 'YbEx']


def amount_format(amount):
    cut_format = 0
    while amount >= 1024:
        amount /= 1024
        cut_format += 1
    return f'{round(amount, 2)} {NAME_AMOUNT_FORMAT[cut_format]}'

def get_path(path: str) -> str:
    file = ''
    is_file = path[-1] != '/'
    dirs = path.split('/')
    if is_file:
        file = dirs[-1]
        dirs = dirs[:-1]

    path = os.path.join(os.path.abspath(os.curdir), *dirs)
    if not os.path.exists(path):
        os.makedirs(path)
    if is_file:
        path = os.path.join(path, file)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write('')
    return path

def exists_path(path: str) -> bool:
    return os.path.exists(os.path.join(os.path.abspath(os.curdir), *path.split('/')))


def get_size_file(path: str) -> int:
    if exists_path(path):
        return os.path.getsize(get_path(path))
    return 0


def get_pools_address():
    return list(LoadJsonFile('data/pool/pools_host').as_dict().keys())


def get_pools_host(path):
    pools = LoadJsonFile(path).as_dict()
    if pools:
        return LoadJsonFile(path).as_dict()
    else:
        return {"": (POOL_ROOT_IP, POOL_PORT, POOL_CM_PORT, POOL_FN_PORT)}


def append_pool_host(name, ip, port_pool, port_cm, port_fn):
    pools = LoadJsonFile('data/pool/pools_host').as_dict()
    pools[name] = (ip, port_pool, port_cm, port_fn)
    SaveJsonFile('data/pool/pools_host', data=pools)


def print_error(*args):
    if ERROR_VIEW:
        print(*args)


def print_info(*args):
    if INFO_VIEW:
        print(*args)


def print_warning(*args):
    if WARNING_VIEW:
        print(*args)


def generate_random_string(length):
    return ''.join(choice(_LETTERS) for _ in range(length))


def get_hash(data):
    return hex(int.from_bytes(sha3_256(bytes(json.dumps(data, sort_keys=True), 'utf-8')).digest(), 'big'))[2:]


def sorted_dict(data):
    return dict(sorted(data.items(), key=lambda x: x[0]))


def is_ttl_file(path):
    return datetime.datetime.now().timestamp() - os.path.getctime(get_path(path)) < TIME_TO_LIFE_FILE


class SaveJsonFile:
    # Сохранение в файлы
    def __init__(self, path: str, data, sort_keys=False):
        # Сначала сохраняем в файл tmp. На тот случай если файл не запишется при сбое. Чтобы можно было восстановить
        rand_string = generate_random_string(8)
        path = get_path(path)
        random_path = f'{path}_{rand_string}.tmp'
        with open(random_path, 'w') as f:
            f.write(json.dumps(data, sort_keys=sort_keys))
        copyfile(random_path, path)
        os.remove(random_path)


class LoadJsonFile:
    # Загрузка из файлов
    def __init__(self, path: str):
        """
        if exists_path(path):
            while True:
                path_rebuild = get_path(path)
                try:
                    with open(path_rebuild, 'r') as f:
                        self._data = json.loads(f.read())  # Выдает ошибку, если некорректный фалй
                    break
                except Exception as e:
                    print(44444444444, e)
                    # Если файл битый(при прощлой записи программа оборвалсь на записи файла),
                    # то загружаем данные из прошлой версии tmp
                    if exists_path(path + '.tmp'):
                        copyfile(path_rebuild + '.tmp', path_rebuild)
                        os.remove(path_rebuild + '.tmp')
                    else:
                        # Если прошлой версии tmp нет - выдаем ошибку
                        raise Exception(f'File {path_rebuild} is damaged')
        else:
            self._data = None
        """
        if exists_path(path):
            path_rebuild = get_path(path)
            flag_open_file = False
            for _ in range(50):
                try:
                    with open(path_rebuild, 'r') as f:
                        self._data = json.loads(f.read())  # Выдает ошибку, если некорректный фалй
                    flag_open_file = True
                    break
                except:
                    time.sleep(0.1)
            if not flag_open_file:
                # Если файл битый(при прощлой записи программа оборвалсь на записи файла),
                # то загружаем данные из прошлой версии tmp
                if exists_path(path + '.tmp'):
                    copyfile(path_rebuild + '.tmp', path_rebuild)
                    os.remove(path_rebuild + '.tmp')
                else:
                    # Если прошлой версии tmp нет - выдаем ошибку
                    raise Exception(f'File {path_rebuild} is damaged')
        else:
            self._data = None

    def as_list(self):
        if type(self._data) is list:
            return self._data
        elif self._data is None:
            return []
        raise Exception('Object is not list')

    def as_dict(self):
        if type(self._data) is dict:
            return self._data
        elif self._data is None:
            return {}
        raise Exception('Object is not dict')

    def as_string(self):
        if type(self._data) is str:
            return self._data
        elif self._data is None:
            return ''
        raise Exception('Object is not string')

    def as_integer(self):
        if type(self._data) is int:
            return self._data
        elif self._data is None:
            return 0
        raise Exception('Object is not integer')

    def as_float(self):
        if type(self._data) is float:
            return self._data
        elif self._data is None:
            return float(0)
        raise Exception('Object is not float')


class DispatcherSaveFiles:
    def __init__(self):
        self._tasks = set()

    def add(self, path, data, sort_keys=False):
        self._tasks.add(path)
        # Сначала сохраняем в файл tmp (обновляем предыдущую версию)
        with open(get_path(path) + '.tmp', 'w') as f:
            f.write(json.dumps(data, sort_keys=sort_keys))

    def commit(self):
        for path in self._tasks:
            path_rebuild = get_path(path)
            # В случае удачного сохранения в tmp - копируем tmp в основной
            copyfile(path_rebuild + '.tmp', path_rebuild)
            os.remove(path_rebuild + '.tmp')
        self._tasks = set()
