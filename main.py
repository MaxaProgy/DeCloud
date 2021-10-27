from plot import Plot
from multiprocessing import Process
import time
from wallet import Wallet


def start_plot(ip_addr_pool, port_pool, private_key):
    plot = Plot(ip_addr_pool, port_pool, private_key)
    plot.start()
    print('Запускаем Plot: ', Wallet(private_key).address)
    file = 'videoplayback_Trim.mp4'  # input('Введите путь к файлу: ')
    plot.load_from_file(file)
    print(f'Загружаем файл {file}')
    plot.save_data(file)
    print(f'Файл {file} загружен')


if __name__ == '__main__':
    private_keys = open('data/key', 'r').readlines()
    if private_keys:
        for private_key in private_keys:
            private_key = private_key[:-1]
            print('Инициализируем Plot: ', Wallet(private_key).address)
            process_plot = Process(target=start_plot, args=("127.0.0.1", 8888, private_key))
            process_plot.start()
    else:
        process_plot = Process(target=start_plot, args=("127.0.0.1", 8888, None))
        process_plot.start()

    while True:
        time.sleep(1)
