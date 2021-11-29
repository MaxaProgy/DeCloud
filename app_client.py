import os
from hashlib import sha3_256
import sys

from PyQt5.QtCore import Qt
import requests
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QDesktopWidget, \
    QPushButton, QListWidget, QInputDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox
from wallet import Wallet


class AppClient(QMainWindow):
    def __init__(self, port):
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
            self.show_current_objects(self._clients[self.clients_lw.currentItem().text()]['id_current_dir'])

    def item_change(self, item):
        self.clients_lw.setCurrentItem(item)
        self.show_current_objects(self._clients[self.clients_lw.currentItem().text()]['id_current_dir'])

    def get_wallet(self):
        wallet = self._clients[self.clients_lw.currentItem().text()]['wallet']
        return wallet

    def signed_data_request(self, data=None):
        if data is None:
            data = {}
        wallet = self.get_wallet()
        if 'json' not in data.keys():
            data['json'] = {}
        data['json']['id_decloud'] = wallet.public_key
        if 'file' in data.keys():
            data['json']['file_hash'] = sha3_256(data['file'][1]).hexdigest()
        data['json']['sign'] = wallet.sign(data['json'])

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
        self.show_current_objects()

    def open_object(self, item):
        name_item = self.explorer.item(self.explorer.currentRow(), 0).text()
        type_item = self.explorer.item(self.explorer.currentRow(), 1).text()
        id_item = self.explorer.item(self.explorer.currentRow(), 2).text()
        if type_item == 'Directory':
            self._clients[self.clients_lw.currentItem().text()]['id_current_dir'] = id_item
        self.show_current_objects(id_item)

    def show_current_objects(self, id_obj=None):
        data = {'id_decloud': self.get_wallet().public_key}
        if id_obj not in {None, ''}:
            data['id_object'] = id_obj

        dct_files_and_directories = requests.get(f'http://127.0.0.1:{self._port}/api/get_object',
                                                 params=data)
        try:
            dct_files_and_directories = dct_files_and_directories.json()
            type_obj = 'dir'
        except:
            type_obj = 'file'
        if type_obj == 'dir':
            self.explorer.clear()
            self.explorer.setRowCount(0)

            if not dct_files_and_directories['parent'] == '':
                self.explorer.setRowCount(1)
                self.explorer.setItem(0, 0, QTableWidgetItem('..'))
                self.explorer.setItem(0, 1, QTableWidgetItem('Directory'))
                self.explorer.setItem(0, 2, QTableWidgetItem(dct_files_and_directories['parent']))

            for type in ['dirs', 'files']:
                for obj in sorted(dct_files_and_directories[type], key=lambda k: k['name']):
                    row = self.explorer.rowCount()
                    self.explorer.setRowCount(row + 1)
                    self.explorer.setItem(row, 0, QTableWidgetItem(obj['name']))
                    self.explorer.setItem(row, 1, QTableWidgetItem({'dirs': 'Directory', 'files': 'File'}[type]))
                    self.explorer.setItem(row, 2, QTableWidgetItem(obj['id_object']))
        else:
            file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     'data', 'cloud', 'temp', self.explorer.currentItem().text())
            with open(file_name, 'w') as f:
                f.write(dct_files_and_directories.text)
            os.system("start " + file_name)

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
                    data = {'json': {'name': text}}
                    id_current_dir = self._clients[self.clients_lw.currentItem().text()]['id_current_dir']
                    if id_current_dir:
                        data['json']['id_current_dir'] = id_current_dir
                    data = self.signed_data_request(data)

                    response = requests.get(f'http://127.0.0.1:{self._port}/api/make_dir',
                                            params=data['json']).json()
                    if 'error' in response:
                        QMessageBox.critical(self, "Error", response['error'], QMessageBox.Ok)
                    else:
                        self.show_current_objects(id_current_dir)

    def send_file(self):
        if self.clients_lw.count() == 0:
            QMessageBox.critical(self, "Ошибка", "Нет клиента", QMessageBox.Ok)
        else:
            file_name = QFileDialog.getOpenFileName(self, "Select a file...", None, filter="All files (*)")[0]
            if file_name != "":
                print(f'Загружаем файл {file_name}')
                data = {'file': (file_name.split('/')[-1], open(file_name, 'rb').read()), 'json': {}}
                id_current_dir = self._clients[self.clients_lw.currentItem().text()]['id_current_dir']
                if id_current_dir:
                    data['json']['id_current_dir'] = id_current_dir
                data = self.signed_data_request(data)
                response = requests.post(f'http://127.0.0.1:{self._port}/api/save_file', files={'file': data['file']},
                                         params=data['json']).json()
                if 'error' in response:
                    QMessageBox.critical(self, "Error", response['error'], QMessageBox.Ok)
                else:
                    self.show_current_objects(id_current_dir)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_manger = AppClient(4545)
    client_manger.show()
    sys.exit(app.exec_())
