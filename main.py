from plot import Plot
from blockchain import blockchain
from multiprocessing import Process
import time
from wallet import Wallet


def start_plot(ip_addr, port):
    private_key = open('data/key', 'r').readline()[:-1]
    print('Инициализируем Plot: ', Wallet(private_key).address)
    plot = Plot(ip_addr, port, private_key)
    print('Запускаем Plot: ', Wallet(private_key).address)
    plot.start()


if __name__ == '__main__':
    process_plot = Process(target=start_plot, args=("127.0.0.1", 5000))
    process_plot.start()
    time.sleep(10)
    process_plot1 = Process(target=start_plot, args=("127.0.0.1", 5001))
    process_plot1.start()
    while True:
        time.sleep(1)
