import time
from multiprocessing import cpu_count
from multiprocessing import Process

from dctp1 import ServerDCTP, ClientDCTP
from fog_node import FogNode
from utils import get_path


class ManagerFogNodes():
    def __init__(self):
        self._cpu_count = cpu_count()
        self._count_fog_nodes = 0
        self._server_fog_nodes = None
        self.run_server()
        self.load_fog_nodes()

    @staticmethod
    def worker_process(cpu, port):
        worker = ClientDCTP('PROCESS WORKER ' + str(cpu), '127.0.0.1', port)

        @worker.method('add_fog_node')
        def add_fog_node(data):
            fog_node = FogNode(worker, data['private_key'])
            fog_node.start()

        worker.start()

    def run_server(self):
        self._server_fog_nodes = ServerDCTP()

        @self._server_fog_nodes.method('current_state_fog_node')
        def current_state_fog_node(data):
            try:
                while True:
                    self.on_change_state(data)
                    break
            except:
                pass

        self._server_fog_nodes.start()
        for cpu in range(cpu_count()):
            t = Process(target=self.worker_process, args=[cpu, self._server_fog_nodes.current_port])
            t.start()
        time.sleep(6)

    def on_change_state(self, data):
        pass

    def load_fog_nodes(self):
        with open(get_path(dirs=['data', 'fog_nodes'], file='key'), 'r') as f:
            for key in f.readlines():
                self.add_fog_node(key[:-1])

    def add_fog_node(self, private_key=None):
        self._count_fog_nodes += 1
        self._server_fog_nodes.request(f'PROCESS WORKER {self._count_fog_nodes % self._cpu_count}', 'add_fog_node',
                                       data={'private_key': private_key})