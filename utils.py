import os
import json
from shutil import copyfile

ERROR_VIEW = True
INFO_VIEW = True
WARNING_VIEW = True


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
    return os.path.getsize(get_path(path))


def get_pools_address():
    return list(LoadJsonFile('data/pool/pools_host').as_dict().keys())


def get_my_ip():
    return '127.0.0.1'
    """
    import urllib.request
    import re
    
    res = urllib.request.urlopen('http://2ip.ru/').read()
    return re.search(b'\d+\.\d+\.\d+\.\d+', res).group().decode("utf-8"))
    """


def get_pools_host(path):
    return LoadJsonFile(path).as_dict()


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


class SaveJsonFile:
    # Сохранение в файлы
    def __init__(self, path: str, data):
        path = get_path(path)
        # Сначала сохраняем в файл tmp (обновляем предыдущую версию)
        with open(path + '.tmp', 'w') as f:
            f.write(json.dumps(data, sort_keys=True))
        copyfile(path + '.tmp', path)
        os.remove(path + '.tmp')


class LoadJsonFile:
    # Загрузка из файлов
    def __init__(self, path: str):
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

    def add(self, path, data):
        self._tasks.add(path)
        # Сначала сохраняем в файл tmp (обновляем предыдущую версию)
        with open(get_path(path) + '.tmp', 'w') as f:
            f.write(json.dumps(data, sort_keys=True))

    def commit(self):
        for path in self._tasks:
            path_rebuild = get_path(path)
            # В случае удачного сохранения в tmp - копируем tmp в основной
            copyfile(path_rebuild + '.tmp', path_rebuild)
            os.remove(path_rebuild + '.tmp')
        self._tasks = set()
