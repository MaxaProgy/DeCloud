import os
import json

POOL_ROOT_IP = '127.0.0.1'
from variables import POOL_CSM_PORT, POOL_FN_PORT


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


def _read_pools_host():
    if not exists_path(dirs=['data', 'pool'], file='pools_host'):
        return {}

    with open(get_path(dirs=['data', 'pool'], file='pools_host'), 'r') as f:
        return json.loads(f.read())


def get_pools_address():
    return list(_read_pools_host().keys())


def get_pools_host():
    pools = _read_pools_host()
    if pools:
        return [(pools[key]) for key in pools]
    else:
        return [(POOL_ROOT_IP, POOL_CSM_PORT, POOL_FN_PORT)]


def append_pool_host(name, ip, port_csm, port_fn):
    pools = _read_pools_host()
    pools[name] = (ip, port_csm, port_fn)
    with open(get_path(dirs=['data', 'pool'], file='pools_host'), 'w') as f:
        f.write(json.dumps(pools))
