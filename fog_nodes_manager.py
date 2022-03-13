from multiprocessing import cpu_count, Process
from dctp import ServerDCTP, ClientDCTP
from fog_node import FogNode
from utils import LoadJsonFile
from wallet import Wallet


class WorkerProcess(Process):
    def __init__(self, process_name, port):
        super().__init__()
        self.process_name = process_name
        self._port = port
        self.fog_nodes = {}
        self.client = None

    def run(self):
        self.client = ClientDCTP(self.process_name, '127.0.0.1', self._port)

        @self.client.method('add_fog_node')
        def add_fog_node(data):
            self.fog_nodes[data['address']] = FogNode(self.client, data['private_key'])
            self.fog_nodes[data['address']].start()

        @self.client.method('get_balance')
        def get_balance(data):
            return self.fog_nodes[data['address']].pool_client.request(data['address'], 'get_balance')

        self.client.start()


class ManagerFogNodes:
    def __init__(self, cpu_count=cpu_count()):
        self.process_worker = []
        self._cpu_count = cpu_count
        self._count_fog_nodes = 0
        self._server_fog_nodes = None
        self.run_server()

    def run_server(self):
        self._server_fog_nodes = ServerDCTP()

        @self._server_fog_nodes.method('current_state_fog_node')
        def current_state_fog_node(json, data):
            self.on_change_state(json)

        @self._server_fog_nodes.method('update_balance_fog_node')
        def update_balance_fog_node(json, data):
            self.on_change_balance(json)

        self._server_fog_nodes.start()

        for cpu in range(self._cpu_count):
            process_name = f'Process_FNM_{Wallet().address}'
            self.process_worker.append({'process_name': process_name, 'process_clients': []})
            worker = WorkerProcess(process_name, self._server_fog_nodes.current_port)
            worker.start()

    def on_change_state(self, data):
        pass

    def on_change_balance(self, data):
        pass

    def load_fog_nodes(self, path):
        for key in LoadJsonFile(path).as_list():
            self.add_fog_node(key)

    def add_fog_node(self, private_key=None):
        address = Wallet(private_key).address
        self.process_worker[self._count_fog_nodes % self._cpu_count]['process_clients'].append(address)
        self.request(address, 'add_fog_node', data={'private_key': private_key})
        self._count_fog_nodes += 1

    def request(self, address, method, data=None):
        if data is None:
            data = {}
        for worker in self.process_worker:
            if address in worker['process_clients']:
                data['address'] = address
                return self._server_fog_nodes.request(worker['process_name'], method=method, data=data)
