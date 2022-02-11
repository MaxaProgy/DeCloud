from multiprocessing import cpu_count
from utils import get_path


class ManagerStorages():
    def __init__(self, server):
        self._cpu_count = cpu_count()
        self._count_storages = 0
        self._server = server
        self.load_storages()

    def load_storages(self):
        with open(get_path(dirs=['data', 'storages'], file='key'), 'r') as f:
            for key in f.readlines():
                self.add_storage(key[:-1])

    def add_storage(self, private_key=None):
        self._count_storages += 1
        self._server.request(f'WORKER {self._count_storages % self._cpu_count}', 'add_storage', data={'private_key': private_key})


