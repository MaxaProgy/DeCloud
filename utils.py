import os
import time

POOL_CSM_PORT = 4914
POOL_FN_PORT = 4913

hosts_pool_fn = {}
hosts_pool_csm = {}


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


def get_pools_address():
    return list(hosts_pool_fn.keys())

def get_pools_csm_host():
    while not hosts_pool_csm:
        time.sleep(1)
    return hosts_pool_csm[list(hosts_pool_csm.keys())[0]]


def get_pools_fn_host():
    while not hosts_pool_fn:
        time.sleep(1)
    return hosts_pool_fn[list(hosts_pool_fn.keys())[0]]


def set_pools_fn_host(name, ip, port):
    hosts_pool_fn[name] = (ip, port)


def set_pools_csm_host(name, ip, port):
    hosts_pool_csm[name] = (ip, port)
