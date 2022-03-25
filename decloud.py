import sys
from fog_nodes_manager import ManagerFogNodes
from variables import POOL_PORT,POOL_FN_PORT,POOL_CM_PORT,PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME, DNS_IP
from PyQt5.QtWidgets import QApplication
from command_parser import CommandParser
from app_client import AppClient
from clients_manager import DispatcherClientsManager
from pool import Pool
import ctypes
import os


def RegisterDomainName():
    os_name = os.name
    if os_name == 'nt':
        path = os.environ['SYSTEMROOT'] + '\System32\drivers\etc\hosts'
    elif os_name == 'posix':
        path = '/etc/hosts'
        run_admin = True

        with open(path, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line[:-1] == DNS_IP + ' ' + DNS_NAME:
                    run_admin = False

        print(run_admin, ctypes.windll.shell32.IsUserAnAdmin())
        if run_admin:
            if os_name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
                hinstance = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join(sys.argv), None, 1)
                exit(0)
            elif os_name == 'posix' and os.getuid() != 0:
                print('Please input SUDO')
                exit(0)
            else:
                with open(path, 'a') as f:
                    f.write('\n' + DNS_IP + ' ' + DNS_NAME + '\n')


if __name__ == '__main__':
    RegisterDomainName()

    if 'console' in sys.argv or '-c' in sys.argv:
        parser = CommandParser()
        parser.add_command('create_pool')
        parser.add_argument('create_pool', '--port_pool', default=POOL_PORT)
        parser.add_argument('create_pool', '--port_cm', default=POOL_CM_PORT)
        parser.add_argument('create_pool', '--port_fn', default=POOL_FN_PORT)

        parser.add_command('create_fog_node')

        mfn = ManagerFogNodes()
        mfn.load_fog_nodes('data/fog_nodes/key')
        while True:
            print("(DECLOUD) >> ", end='')
            result = parser.parse_string(input())
            if result:
                if result[0] == 'create_pool':
                    params = result[1]
                    pool = Pool(port_pool=params['--port_pool'], port_cm=params['--port_cm'], port_fn=params['--port_fn'])
                    pool.start()
                if result[0] == 'create_fog_node':
                    mfn.add_fog_node()
            else:
                print('Неизвестная команда')

    else:
        app = QApplication(sys.argv)
        dispatcher = DispatcherClientsManager(PORT_DISPATCHER_CLIENTS_MANAGER)
        dispatcher.start()

        client_manager = AppClient()
        client_manager.show()
        sys.exit(app.exec_())
# create_pool --port_pool 2323 --port_cm 2324 --port_fn 2325
# decloud.py -c True