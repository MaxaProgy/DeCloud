from multiprocessing import cpu_count, Process
from dctp import ServerDCTP, ClientDCTP
from fog_node import FogNode
from utils import LoadJsonFile
from wallet import Wallet
from threading import Thread

class WorkerProcess(Process):
    def __init__(self, process_name, port):
        super().__init__()
        self.process_name = process_name
        self._port = port
        self.fog_nodes = {}
        self.client = None

    def run(self):
        self.client = ClientDCTP(self.process_name, reconnect=True)

        @self.client.method('start_fog_node')
        def start_fog_node(request):
            self.fog_nodes[request.json['address']] = FogNode(self.client, request.json['private_key'])
            self.fog_nodes[request.json['address']].start()

        @self.client.method('get_balance')
        def get_balance(request):
            return self.fog_nodes[request.json['address']].pool_client.request(method='get_balance').json

        @self.client.method('stop')
        def stop(request):
            from time import sleep

            [self.fog_nodes[address].stop() for address in self.fog_nodes]
            while sum([self.fog_nodes[address].is_alive() for address in self.fog_nodes]) != 0:
                sleep(0.1)

            self.client.disconnect()

        self.client.connect('127.0.0.1', self._port)


class ManagerFogNodes():
    def __init__(self, cpu_count=cpu_count()):
        self.process_worker = []
        self._cpu_count = cpu_count
        self._count_fog_nodes = 0
        self._server_fog_nodes = None
        self.run_server()

    def run_server(self):
        self._server_fog_nodes = ServerDCTP()

        @self._server_fog_nodes.method('current_state_fog_node')
        def current_state_fog_node(request):
            self.on_change_state(request)

        @self._server_fog_nodes.method('update_balance_fog_node')
        def update_balance_fog_node(request):
            self.on_change_balance(request)

        self._server_fog_nodes.start()
        for cpu in range(self._cpu_count):
            process_name = f'Process_FNM_{Wallet().address}'
            self.process_worker.append({'process_name': process_name, 'process_clients': []})
            worker = WorkerProcess(process_name, self._server_fog_nodes.current_port)
            worker.start()


    def on_change_state(self, request):
        pass

    def on_change_balance(self, request):
        pass

    def load_fog_nodes(self):
        wallets = []
        for key in LoadJsonFile('data/fog_nodes/key').as_list():
            wallet = Wallet(key)
            self.start_fog_node(wallet)
            wallets.append(wallet)
        return wallets

    def create_fog_node(self):
        wallet = Wallet()
        wallet.save_private_key('data/fog_nodes/key')
        return wallet

    def start_fog_node(self, wallet):
        self.process_worker[self._count_fog_nodes % self._cpu_count]['process_clients'].append(wallet.address)
        self._count_fog_nodes += 1
        thread = Thread(target=self.request_start_fog_node, args=[wallet.address, {'private_key': wallet.private_key}])
        thread.start()

    def request_start_fog_node(self, address, json={}):
        from time import sleep

        for worker in self.process_worker:
            if address in worker['process_clients']:
                break
        json['address'] = address
        while True:
            response = self._server_fog_nodes.request(id_worker=worker['process_name'],
                                              method='start_fog_node', json=json)
            if response.status == 0:
                break
            sleep(1)

    def close(self):
        for worker in self.process_worker:
            try:
                self._server_fog_nodes.request(id_worker=worker['process_name'], method="stop")
            except:
                pass
        self._server_fog_nodes.stop()
