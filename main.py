from plot import Plot
from multiprocessing import Process
import time
from wallet import Wallet


def start_plot(ip_addr_pool, port_pool):
    private_key = open('data/key', 'r').readline()[:-1]
    if private_key == '':
        private_key = None
    else:
        print('Инициализируем Plot: ', Wallet(private_key).address)

    plot = Plot(ip_addr_pool, port_pool, private_key)
    print('Запускаем Plot: ', Wallet(private_key).address)
    file = input('Введите путь к файлу: ')
    plot.load_from_file(file)
    print(f'Загружаем файл {file}')
    plot.save_data(file)
    plot.start()


if __name__ == '__main__':
    process_plot = Process(target=start_plot, args=("127.0.0.1", 2222))
    process_plot.start()

    while True:
        time.sleep(1)
