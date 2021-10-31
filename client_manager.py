import sys

from PyQt5.QtCore import Qt

from storage import ClientCloud
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QDesktopWidget, QPushButton, QListWidget

from wallet import Wallet


class ClientManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.geometry = QDesktopWidget().availableGeometry()
        self.setGeometry(1000, 1000, 800, 600)
        self.move(500, 200)
        self.initUI()

    def initUI(self):
        self.btn_open_file = QPushButton('Open file', self)
        self.btn_open_file.move(50, 50)
        self.btn_open_file.clicked.connect(self.open_file)

        self.clients_lw = QListWidget(self)
        self.clients_lw.move(50, 100)
        self.clients_lw.resize(550, 250)
        self.clients_lw.addItems(list(cloud_clients.keys()))
        self.clients_lw.sortItems(Qt.AscendingOrder)
        if self.clients_lw.count() > 0:
            self.clients_lw.setCurrentItem(self.clients_lw.item(0))

    def open_file(self):
        fname = QFileDialog.getOpenFileName(self, "Select a file...", None, filter="All files (*)")[0]
        client = cloud_clients[self.clients_lw.currentItem().text()]
        print(f'Загружаем файл {fname}')
        client.load_from_file(fname)


if __name__ == '__main__':
    private_keys = [key[:-1] for key in open('data/storages/key', 'r').readlines()]
    cloud_clients = {}
    for private_key in private_keys:
        client = ClientCloud("127.0.0.1", 4444, private_key)
        cloud_clients[Wallet(private_key).address] = client

    app = QApplication(sys.argv)
    client_manger = ClientManager()
    client_manger.show()
    sys.exit(app.exec_())
