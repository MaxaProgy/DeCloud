import multiprocessing
import sys
from argparse import ArgumentParser
from variables import POOL_PORT, POOL_FN_PORT, POOL_CM_PORT
from register_domain_name import register_domain_name


if __name__ == '__main__':
    multiprocessing.freeze_support()
    #register_domain_name()

    parser = ArgumentParser()

    parser.add_argument('-c', '--console', action="store_true", help='concole mode')
    parser.add_argument('-ppl', '--port_pool', default=POOL_PORT, type=int, help='port to listen pool')
    parser.add_argument('-pcm', '--port_cm', default=POOL_CM_PORT, type=int,
                        help='port to listen pool clients manager')
    parser.add_argument('-pfn', '--port_fn', default=POOL_FN_PORT, type=int, help='port to listen pool fog nodes')

    args = parser.parse_args()

    if args.console:
        from fog_nodes_manager import ManagerFogNodes
        from command_parser import CommandParser


        parser = CommandParser()
        parser.add_command('create_pool')
        parser.add_argument('create_pool', '--port_pool', default=POOL_PORT)
        parser.add_argument('create_pool', '--port_cm', default=POOL_CM_PORT)
        parser.add_argument('create_pool', '--port_fn', default=POOL_FN_PORT)

        parser.add_command('create_fog_node')

        mfn = ManagerFogNodes()
        mfn.load_fog_nodes()
        while True:
            print("(DECLOUD) >> ", end='')
            result = parser.parse_string(input())
            if result:
                if result[0] == 'create_pool':
                    from pool import Pool

                    params = result[1]
                    pool = Pool(port_pool=params['--port_pool'], port_cm=params['--port_cm'],
                                port_fn=params['--port_fn'])
                    pool.start()
                if result[0] == 'create_fog_node':
                    mfn.add_fog_node()
            else:
                print('Неизвестная команда')

    else:
        from app_client import AppClient
        from PyQt5.QtWidgets import QApplication

        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("decloud")
        except:
            pass
        app = QApplication(sys.argv)
        client_manager = AppClient(args.port_pool, args.port_cm, args.port_fn)
        client_manager.show()
        sys.exit(app.exec_())

# decloud.py --console
# create_pool --port_pool 2323 --port_cm 2324 --port_fn 2325
