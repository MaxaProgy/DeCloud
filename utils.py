from datetime import datetime, timedelta
import os
import json
from shutil import copy2
from time import sleep
from _pysha3 import keccak_256 as sha3_256
from variables import POOL_ROOT_EXTERNAL_IP, POOL_ROOT_INTERNAL_IP, POOL_PORT, POOL_CM_PORT, POOL_FN_PORT
from string import ascii_lowercase
from random import choice
import requests

ERROR_VIEW = True
INFO_VIEW = True
WARNING_VIEW = True

_LETTERS = ascii_lowercase
NAME_AMOUNT_FORMAT = ['bEx', 'KbEx', 'MbEx', 'GbEx', 'TbEx', 'PbEx', 'EbEx', 'ZbEx', 'YbEx']


class HostParams():
    def __init__(self):
        super().__init__()
        self._external_ip, self._internal_ip = self.get_my_hosts()

    def get_my_hosts(self):
        import socket
        from time import sleep
        from random import random

        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 1))
                int_ip = s.getsockname()[0]
                s.close()

                for address, params in load_pools_host().items():
                    try:
                        ext_ip = requests.get(f'http://{params[0][0]}:{params[1]}/get_my_ip', timeout=0.1).json()
                    except:
                        continue
                    if ext_ip != int_ip:
                        break
                else:
                    ext_ip = requests.get("http://ifconfig.me/ip").text

                return ext_ip, int_ip
            except:
                print("No connection")
                sleep(1)

    def select_host(self, external_ip, internal_ip):
        if self._external_ip == external_ip:
            return internal_ip
        return external_ip


class SyncTime(HostParams):
    def __init__(self):
        super().__init__()
        self.delta = 0

    def sync_time(self):
        hosts = {}
        for address, item in load_pools_host().items():
            if self._external_ip != item[0][0] and item[0][0] not in hosts:
                hosts[item[0][0]] = item[1]
            elif self._internal_ip != item[0][1] and item[0][1] not in hosts:
                hosts[item[0][1]] = item[1]

        if hosts:
            ip_list = list(hosts)
            while True:
                ip = choice(ip_list)
                start_time = datetime.utcnow().timestamp()
                try:
                    time = requests.get(f'http://{ip}:{hosts[ip]}/get_sync_time', timeout=0.5).json()
                except:
                    continue
                end_time = datetime.utcnow().timestamp()
                if type(time) == float:
                    self.delta = time - (start_time + (end_time - start_time) / 2)
                    break

    def sync_utcnow_timestamp(self):
        return datetime.utcnow().timestamp() + self.delta

    def sync_utcnow(self):
        return datetime.utcnow() + timedelta(seconds=self.delta)


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


def load_pools_host():
    pools = LoadJsonFile('data/hosts').as_dict()
    if pools:
        return pools
    return {"": ((POOL_ROOT_EXTERNAL_IP, POOL_ROOT_INTERNAL_IP), POOL_PORT, POOL_CM_PORT, POOL_FN_PORT)}


def save_pools_host(pools):
    if '' in pools.keys():
        pools.pop('')
    SaveJsonFile('data/hosts', pools)


def get_random_pool_host():
    pools = load_pools_host()
    return pools[choice(list(pools))]


def append_pool_host(name:str, hosts:list, port_pool:int, port_cm:int, port_fn:int):
    pools = LoadJsonFile('data/hosts').as_dict()
    for key in list(pools):
        if json.dumps(pools[key]) == json.dumps((hosts, port_pool, port_cm, port_fn)):
            pools.pop(key)
    pools[name] = (hosts, port_pool, port_cm, port_fn)
    save_pools_host(pools)


def print_error(*args):
    if ERROR_VIEW:
        print(*args)


def print_info(*args):
    with open(get_path('data/logs/info.log'), 'a') as f:
        [f.write(str(arg) + ' ') for arg in args]
        f.write('\n')

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


def is_ttl_file(path, ttl):
    return datetime.now().timestamp() - os.path.getatime(path) < ttl


class SaveJsonFile:
    # Сохранение в файлы
    def __init__(self, path: str, data, sort_keys=False):
        # Сначала сохраняем в файл tmp. На тот случай если файл не запишется при сбое. Чтобы можно было восстановить
        rand_string = generate_random_string(8)
        path = get_path(path)
        random_path = f'{path}_{rand_string}.tmp'
        with open(random_path, 'w') as f:
            f.write(json.dumps(data, sort_keys=sort_keys))
        copy2(random_path, path)
        os.remove(random_path)


class LoadJsonFile:
    # Загрузка из файлов
    def __init__(self, path: str):
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
                    sleep(0.1)
            if not flag_open_file:
                # Если файл битый(при прощлой записи программа оборвалсь на записи файла),
                # то загружаем данные из прошлой версии tmp
                if exists_path(path + '.tmp'):
                    copy2(path_rebuild + '.tmp', path_rebuild)
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
        self._tasks.add(path + '.tmp')
        # Сначала сохраняем в файл tmp (обновляем предыдущую версию)
        with open(get_path(path + '.tmp'), 'w') as f:
            f.write(json.dumps(data, sort_keys=sort_keys))

    def commit(self):
        for path in self._tasks:
            path_rebuild = get_path(path)
            # В случае удачного сохранения в tmp - копируем tmp в основной
            copy2(path_rebuild, path_rebuild[:-4])
            os.remove(path_rebuild)
        self._tasks = set()
