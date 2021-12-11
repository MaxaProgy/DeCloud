import os
import sys

from PyQt5.QtCore import Qt
import requests
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QDesktopWidget, \
    QPushButton, QListWidget, QInputDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox
from wallet import Wallet

SIZE_REPLICA = 1024 ** 2

class AppClient(QMainWindow):
    def __init__(self, port=7000):
        super().__init__()
        self._port = port
        self.geometry = QDesktopWidget().availableGeometry()
        self.setGeometry(1000, 1000, 1000, 800)
        self.move(500, 100)
        self.initUI()

    def initUI(self):
        self.btn_send_file = QPushButton('Send file', self)
        self.btn_send_file.move(50, 50)
        self.btn_send_file.clicked.connect(self.send_file)

        self.btn_create_client = QPushButton('Add new client', self)
        self.btn_create_client.move(200, 50)
        self.btn_create_client.clicked.connect(self.create_client)

        self.btn_cleate_dir = QPushButton('Create directory', self)
        self.btn_cleate_dir.move(50, 100)
        self.btn_cleate_dir.clicked.connect(self.create_dir)

        self.clients_lw = QListWidget(self)
        self.clients_lw.move(50, 150)
        self.clients_lw.resize(550, 250)
        private_keys = [key[:-1] for key in open('data/cloud/key', 'r').readlines()]
        self._clients = {}
        for key in private_keys:
            wallet = Wallet(key)
            self._clients[wallet.address] = {'wallet': wallet, 'id_current_dir': None}
        self.clients_lw.addItems(list(self._clients.keys()))
        self.clients_lw.sortItems(Qt.AscendingOrder)
        if self.clients_lw.count() > 0:
            self.clients_lw.setCurrentItem(self.clients_lw.item(0))
            # self.login()
        self.clients_lw.itemClicked.connect(self.item_change)

        self.explorer = QTableWidget(self)
        self.explorer.move(620, 50)
        self.explorer.resize(350, 700)
        labels = ['Name', 'Type', 'Id']
        self.explorer.setColumnCount(len(labels))
        self.explorer.setHorizontalHeaderLabels(labels)
        self.explorer.verticalHeader().hide()
        self.explorer.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.explorer.setShowGrid(False)
        [self.explorer.setColumnWidth(i, 175) for i in range(2)]
        self.explorer.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.explorer.setSelectionMode(QAbstractItemView.SingleSelection)
        self.explorer.itemDoubleClicked.connect(self.open_object)
        if private_keys:
            self.show_current_dir(self._clients[self.clients_lw.currentItem().text()]['id_current_dir'])

    @staticmethod
    def chunking(file_name):
        size_file = os.stat(file_name).st_size
        with open(file_name, 'rb') as f:
            count = 0
            while True:
                data = f.read(SIZE_REPLICA)
                if not data:
                    break
                count += 1
                print((count * 100) // (size_file // SIZE_REPLICA + (size_file % SIZE_REPLICA != 0)), "%")
                yield data

    def item_change(self, item):
        self.clients_lw.setCurrentItem(item)
        self.show_current_dir(self._clients[self.clients_lw.currentItem().text()]['id_current_dir'])

    def get_wallet(self):
        wallet = self._clients[self.clients_lw.currentItem().text()]['wallet']
        return wallet

    def signed_data_request(self, data=None):
        if data is None:
            data = {}
        wallet = self.get_wallet()
        data['public_key'] = wallet.public_key
        data['address'] = wallet.address
        data['sign'] = wallet.sign(data)

        return data

    def create_client(self):
        wallet = Wallet()
        wallet.save_private_key_cloud()

        address = wallet.address
        self._clients[address] = {'wallet': wallet, 'id_current_dir': None}
        self.clients_lw.addItem(address)

        if self.clients_lw.count() == 1:
            self.clients_lw.setCurrentItem(self.clients_lw.item(0))
        else:
            self.clients_lw.setCurrentItem(self.clients_lw.item(self.clients_lw.count() - 1))
        self.show_current_dir()

    def open_object(self, item):
        name_item = self.explorer.item(self.explorer.currentRow(), 0).text()
        type_item = self.explorer.item(self.explorer.currentRow(), 1).text()
        id_item = self.explorer.item(self.explorer.currentRow(), 2).text()
        if type_item == 'Directory':
            self._clients[self.clients_lw.currentItem().text()]['id_current_dir'] = id_item
            self.show_current_dir(id_item)
        else:
            self.show_current_file(id_item)

    def show_current_dir(self, id_obj=None):
        data = {'address': self.get_wallet().address}
        if id_obj not in {None, ''}:
            data['id_object'] = id_obj

        response = requests.get(f'http://127.0.0.1:{self._port}/api/get_object', params=data).json()
        self.explorer.clear()
        self.explorer.setRowCount(0)

        for type in ['dirs', 'files']:
            for obj in sorted(response[type], key=lambda k: k['name']):
                row = self.explorer.rowCount()
                self.explorer.setRowCount(row + 1)
                self.explorer.setItem(row, 0, QTableWidgetItem(obj['name']))
                self.explorer.setItem(row, 1, QTableWidgetItem({'dirs': 'Directory', 'files': 'File'}[type]))
                self.explorer.setItem(row, 2, QTableWidgetItem(obj['id_object']))

    def show_current_file(self, id_obj):
        data = {'address': self.get_wallet().address}
        if id_obj not in {None, ''}:
            data['id_object'] = id_obj

        response = requests.get(f'http://127.0.0.1:{self._port}/api/get_object',
                                                 params=data)
        file_name = os.path.join(os.environ['TEMP'], self.explorer.item(self.explorer.currentRow(), 0).text())
        with open(file_name, 'wb') as f:
            [f.write(chunk) for chunk in response.iter_content(SIZE_REPLICA)]

        os.startfile(file_name)

    def create_dir(self):
        if self.clients_lw.count() == 0:
            QMessageBox.critical(self, "Ошибка", "Нет клиента", QMessageBox.Ok)
        else:
            text, ok = QInputDialog.getText(self, 'Input Dialog',
                                            'Enter name directory:')
            if ok:
                if text == '..':
                    QMessageBox.critical(self, "Ошибка", "Не корректное имя файла", QMessageBox.Ok)
                else:
                    data = {'name': text}
                    id_current_dir = self._clients[self.clients_lw.currentItem().text()]['id_current_dir']
                    if id_current_dir:
                        data['id_current_dir'] = id_current_dir
                    data = self.signed_data_request(data)

                    response = requests.get(f'http://127.0.0.1:{self._port}/api/make_dir',
                                            json=data).json()
                    if 'error' in response:
                        QMessageBox.critical(self, "Error", response['error'], QMessageBox.Ok)
                    else:
                        self.show_current_dir(id_current_dir)

    def send_file(self):
        if self.clients_lw.count() == 0:
            QMessageBox.critical(self, "Ошибка", "Нет клиента", QMessageBox.Ok)
        else:
            path = QFileDialog.getOpenFileName(self, "Select a file...", None, filter="All files (*)")[0]
            if path != "":
                file_name = path.split('/')[-1]
                for i in range(self.explorer.rowCount()):
                    if self.explorer.item(i, 0).text() == file_name and self.explorer.item(i, 1).text() == 'File':
                        QMessageBox.critical(self, "Ошибка", "Такое имя файла уже существует", QMessageBox.Ok)
                        return

                print(f'Загружаем файл {file_name}')
                params = {'file_name': file_name}

                id_current_dir = self._clients[self.clients_lw.currentItem().text()]['id_current_dir']
                if id_current_dir:
                    params['id_current_dir'] = id_current_dir

                params = self.signed_data_request(params)

                response = requests.post(f'http://127.0.0.1:{self._port}/api/save_file', params=params,
                                         data=self.chunking(path)).json()
                if 'error' in response:
                    QMessageBox.critical(self, "Error", response['error'], QMessageBox.Ok)
                else:
                    self.show_current_dir(id_current_dir)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_manger = AppClient()
    client_manger.show()
    sys.exit(app.exec_())
