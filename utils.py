import os
import json
from variables import POOL_CSM_PORT, POOL_FN_PORT
from shutil import copyfile

ERROR_VIEW = True
INFO_VIEW = True
POOL_ROOT_IP = '127.0.0.1'


def get_path(dirs, file=None):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), *dirs)
    if not os.path.exists(path):
        os.makedirs(path)
    if file:
        path = os.path.join(path, file)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write('')
    return path


def make_dirs(*args):
    get_path(dirs=args)


def exists_path(dirs, file=None):
    if file:
        return os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), *dirs, file))
    return os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), *dirs))


def get_size_file(dirs, file):
    return os.path.getsize(get_path(dirs=dirs, file=file))


def get_pools_address():
    return list(LoadJsonFile(dirs=['data', 'pool'], file='pools_host').as_dict().keys())


def get_pools_host():
    pools = LoadJsonFile(dirs=['data', 'pool'], file='pools_host').as_dict()
    if pools:
        return [(pools[key]) for key in pools]
    else:
        return [(POOL_ROOT_IP, POOL_CSM_PORT, POOL_FN_PORT)]


def append_pool_host(name, ip, port_csm, port_fn):
    pools = LoadJsonFile(dirs=['data', 'pool'], file='pools_host').as_dict()
    pools[name] = (ip, port_csm, port_fn)
    SaveJsonFile(dirs=['data', 'pool'], file='pools_host', data=pools)


def print_error(*args):
    if ERROR_VIEW:
        print(*args)


def print_info(*args):
    if INFO_VIEW:
        print(*args)


class SaveJsonFile:
    def __init__(self, dirs: list, file: str, data):
        self._dirs = dirs
        self._file = file
        path = get_path(dirs=dirs, file=file)
        with open(path + '.tmp', 'w') as f:
            f.write(json.dumps(data))
        copyfile(path + '.tmp', path)
        #os.remove(path + '.tmp')


class LoadJsonFile:
    def __init__(self, dirs: list, file: str):
        self._dirs = dirs
        self._file = file
        if exists_path(dirs=dirs, file=file):
            while True:
                path = get_path(dirs=dirs, file=file)
                try:
                    with open(path, 'r') as f:
                        self._data = json.loads(f.read())
                    break
                except:
                    if exists_path(dirs=dirs, file=file + '.tmp'):
                        copyfile(path + '.tmp', path)
                        os.remove(path + '.tmp')
                    else:
                        raise Exception(f'File {path} is damaged')
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
