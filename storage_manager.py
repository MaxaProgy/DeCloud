import time
from multiprocessing import cpu_count
from multiprocessing import Process

from dctp1 import ServerDCTP, ClientDCTP
from storage import Storage
from utils import get_path


class ManagerStorages():
    def __init__(self):
        self._cpu_count = cpu_count()
        self._count_storages = 0
        self._server_storages = None
        self.run_server()
        self.load_storages()

    @staticmethod
    def worker_process(cpu, port):
        worker = ClientDCTP('WORKER ' + str(cpu), '127.0.0.1', port)

        @worker.method('add_storage')
        def add_storage(data):
            storage = Storage(worker, data['private_key'])
            storage.start()

        worker.start()

    def run_server(self):
        self._server_storages = ServerDCTP()

        @self._server_storages.method('current_state_storage')
        def current_state_storage(data):
            try:
                while True:
                    self.on_change_state(data)
                    break
            except:
                pass


        self._server_storages.start()
        for cpu in range(cpu_count()):

            t = Process(target=self.worker_process, args=[cpu, self._server_storages.current_port])
            t.start()
        time.sleep(6)

    def on_change_state(self, data):
        pass

    def load_storages(self):
        with open(get_path(dirs=['data', 'storages'], file='key'), 'r') as f:
            for key in f.readlines():
                self.add_storage(key[:-1])

    def add_storage(self, private_key=None):
        self._count_storages += 1
        self._server_storages.request(f'WORKER {self._count_storages % self._cpu_count}', 'add_storage', data={'private_key': private_key})


