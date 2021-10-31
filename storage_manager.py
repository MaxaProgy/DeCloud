from storage import Storage
from multiprocessing import Process
import time
from wallet import Wallet


def start_storage(ip_addr_pool, port_pool, private_key):
    storage = Storage(ip_addr_pool, port_pool, private_key)
    address = Wallet(private_key).address
    print('Запускаем Storage: ', address)
    storage.start()


if __name__ == '__main__':
    with open('data/storages/key', 'r') as f:
        private_keys = f.read().splitlines()
    if private_keys:
        for private_key in private_keys:
            print('Инициализируем Storage: ', Wallet(private_key).address)
            process_storage = Process(target=start_storage, args=("127.0.0.1", 3333, private_key))
            process_storage.start()
    else:
        process_storage = Process(target=start_storage, args=("127.0.0.1", 3333, None))
        process_storage.start()

    while True:
        time.sleep(1)
