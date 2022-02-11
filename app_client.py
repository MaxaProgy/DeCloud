import os
import sys
import time
from multiprocessing import Process, cpu_count

from PyQt5.QtCore import Qt
import requests
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QDesktopWidget, \
    QPushButton, QListWidget, QInputDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QTabWidget, \
    QFrame, QHBoxLayout, QWidget, QMenu, QAction, QListWidgetItem, QHeaderView, QLabel

from dctp1 import ServerDCTP, ClientDCTP
from storage_manager import ManagerStorages
from utils import get_path
from pool import Pool
from storage import Storage
from wallet import Wallet

SIZE_REPLICA = 1024 ** 2
PATH_POOL_KEY = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'pool', 'key')
POOL_PORT = 2222




class AppClient(QMainWindow):
    def __init__(self, port=7000):
        super().__init__()
        self._port = port

        self._clients = {}
        self._address_pool = None
        self._current_address = None

        self.initUI()
        self._manager = ManagerStorages(server)

    def initUI(self):
        self.geometry = QDesktopWidget().availableGeometry()
        self.setGeometry(1000, 1000, 1000, 800)
        self.move(500, 100)

        tab_cloud = QFrame()
        layout_tab_cloud = QHBoxLayout()

        with open(get_path(dirs=['data', 'cloud'], file='key'), 'r') as f:
            for key in f.readlines():
                wallet = Wallet('cloud', key[:-1])
                if self._current_address is None:
                    self._current_address = wallet.address
                self._clients[wallet.address] = {'wallet': wallet, 'id_current_dir': None}

        self.explorer = QTableWidget()
        labels = ['Name', 'Type', 'Id']
        self.explorer.setColumnCount(len(labels))
        self.explorer.setHorizontalHeaderLabels(labels)
        self.explorer.verticalHeader().hide()
        self.explorer.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.explorer.setShowGrid(False)
        self.explorer.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.explorer.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.explorer.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.explorer.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.explorer.setSelectionMode(QAbstractItemView.SingleSelection)
        self.explorer.itemDoubleClicked.connect(self.open_object)
        if self._clients:
            self.show_current_dir(None)
        self.start_pool()

        layout_tab_cloud.addWidget(self.explorer)
        tab_cloud.setLayout(layout_tab_cloud)

        tab_pool = QFrame()
        self.label_status = QLabel()
        layout_tab_pool = QHBoxLayout()
        layout_tab_pool.addWidget(self.label_status)

        tab_pool.setLayout(layout_tab_pool)

        tab_storages = QFrame()
        layout_tab_storages = QHBoxLayout()

        self.list_storages = QTableWidget()
        labels = ['Name', 'State']
        self.list_storages.setColumnCount(len(labels))
        self.list_storages.setHorizontalHeaderLabels(labels)
        self.list_storages.verticalHeader().hide()
        self.list_storages.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.list_storages.setShowGrid(False)
        self.list_storages.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.list_storages.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.list_storages.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list_storages.setSelectionMode(QAbstractItemView.SingleSelection)
        with open(get_path(dirs=['data', 'storages'], file='key'), 'r') as f:
            for key in f.readlines():
                wallet = Wallet('storage', key[:-1])
                address = wallet.address
                row = self.list_storages.rowCount()
                self.list_storages.setRowCount(row + 1)
                self.list_storages.setItem(row, 0, QTableWidgetItem(address))
                if address in self._clients.keys():
                    self.list_storages.item(row, 0).setForeground(QColor('green'))
        self.list_storages.setSortingEnabled(True)
        self.list_storages.sortByColumn(0, Qt.AscendingOrder)
        self.list_storages.setCurrentCell(0, 0)
        self.list_storages.currentCellChanged.connect(self.current_change_storage)

        layout_tab_storages.addWidget(self.list_storages)
        tab_storages.setLayout(layout_tab_storages)

        self.tab = QTabWidget()
        self.tab.addTab(tab_cloud, "Клиент")
        self.tab.addTab(tab_pool, "Pool")
        self.tab.addTab(tab_storages, "Storages")

        self.tab.currentChanged.connect(self._createMenuBar)
        self.setCentralWidget(self.tab)

        self._createActions()
        self._createMenuBar()

        self.setWindowTitle("DeCloud")
        if self._current_address:
            self.setWindowTitle("DeCloud  —  " + self._current_address)

    def _createActions(self):
        self.newAction = QAction(self)

        self.createStoragesAction = QAction("Create storage", self)
        self.createStoragesAction.triggered.connect(self.create_storage)

        self.createPoolAction = QAction("Create Pool", self)
        self.createPoolAction.triggered.connect(self.connect_pool)

        self.exitAction = QAction("Exit", self)
        self.exitAction.triggered.connect(self.close)

        self.createDirAction = QAction("Create directory", self)
        self.createDirAction.triggered.connect(self.create_dir)

        self.sendFileAction = QAction('Send file', self)
        self.sendFileAction.triggered.connect(self.send_file)

        self.createClientAction = QAction("Create client", self)
        self.createClientAction.setEnabled(False)
        self.createClientAction.triggered.connect(self.create_client)

    def _createMenuBar(self):
        menuBar = self.menuBar()
        menuBar.clear()

        fileMenu = QMenu("File", self)
        menuBar.addMenu(fileMenu)

        if self.tab.currentIndex() == 0:
            self.setWindowTitle("DeCloud  —  " + self._current_address)
            storagesMenu = fileMenu.addMenu("Open Storages")
            self.addressesAction = []
            if not self._clients:
                storagesMenu.setEnabled(False)

            for name in list(self._clients.keys()):
                self.addressesAction.append(QAction(name, self))
                self.addressesAction[-1].triggered.connect(self.change_client_address)
                storagesMenu.addAction(self.addressesAction[-1])

                if self.addressesAction[-1].text() == self._current_address:
                    self.addressesAction[-1].setCheckable(True)
                    self.addressesAction[-1].setChecked(True)
                else:
                    self.addressesAction[-1].setCheckable(False)

        elif self.tab.currentIndex() == 1:
            fileMenu.addAction(self.createPoolAction)

            if self._address_pool:
                self.setWindowTitle("DeCloud  —  " + self._address_pool)
                self.createPoolAction.setEnabled(False)
            else:
                self.setWindowTitle("DeCloud")

        elif self.tab.currentIndex() == 2:
            self.setWindowTitle("DeCloud  —  " + self._current_address)
            self.list_storages.setFocus()
            fileMenu.addAction(self.createStoragesAction)

        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        editMenu = menuBar.addMenu("Edit")
        if self.tab.currentIndex() == 0:
            editMenu.addAction(self.createDirAction)
            editMenu.addAction(self.sendFileAction)
        elif self.tab.currentIndex() == 1:
            pass
        elif self.tab.currentIndex() == 2:
            editMenu.addAction(self.createClientAction)

        helpMenu = menuBar.addMenu("Help")

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
    @staticmethod
    def start_process_pool(private_key):
        try:
            pool = Pool(private_key)
        except Exception as e:
            print(e)

    def start_pool(self):
        if os.path.exists(PATH_POOL_KEY):
            with open(PATH_POOL_KEY) as f:
                private_key = f.readline()
                process_node = Process(target=self.start_process_pool, args=[private_key])
                process_node.start()
                self._address_pool = Wallet("pool", private_key).address
                print(f'Start POOL {self._address_pool}')

    def connect_pool(self):
        wallet = Wallet('pool')
        wallet.generate_private_key()
        wallet.save_private_key()
        print(f'Create POOL {wallet.address}')
        self.createPoolAction.setEnabled(False)
        self.start_pool()

    def create_client(self):
        address = self.list_storages.item(self.list_storages.currentRow(), 0).text()
        with open(get_path(dirs=['data', 'storages'], file='key'), 'r') as f:
            for key in f.readlines():
                wallet = Wallet('storages', key[:-1])
                if wallet.address == address:
                    self._clients[address] = {'wallet': Wallet('cloud', key[:-1]), 'id_current_dir': None}
                    self._clients[address]['wallet'].save_private_key()
                    self.list_storages.item(self.list_storages.currentRow(), 0).setForeground(QColor('green'))
                    self.setWindowTitle("DeCloud  —  " + address)
                    self._current_address = address
                    self.show_current_dir()
                    self.tab.setCurrentIndex(0)
                    self._createMenuBar()
                    return

    def create_storage(self):
        # Создаем новый storage
        self._manager.add_storage()

        """
        storage = Storage()
        address = storage.wallet.address
        storage.start()
        self._storages[address] = {'wallet': Wallet('storage')}
        row = self.list_storages.rowCount()
        self.list_storages.setRowCount(row + 1)
        self.list_storages.setItem(row, 0, QTableWidgetItem(address))
        self.list_storages.sortByColumn(0, Qt.AscendingOrder)
        for i in range(row):
            if self.list_storages.item(i, 0).text() == address:
                self.list_storages.setCurrentCell(i, 0)
                break"""

    def current_change_storage(self, row):
        self.createClientAction.setEnabled(self.list_storages.item(row, 0).text() not in self._clients.keys())

    def change_client_address(self):
        self._current_address = self.sender().text()
        [addressAction.setCheckable(False) for addressAction in self.addressesAction]
        self.sender().setCheckable(True)
        self.sender().setChecked(True)
        self.setWindowTitle("DeCloud  —  " + self._current_address)
        self.show_current_dir()

    def get_current_client_wallet(self):
        # Получить кошелек
        wallet = self._clients[self._current_address]['wallet']
        return wallet

    def signed_data_request(self, data=None):
        # Формируем request и подписываем
        if data is None:
            data = {}
        wallet = self.get_current_client_wallet()
        data['public_key'] = wallet.public_key
        data['address'] = wallet.address
        data['sign'] = wallet.sign(data)

        return data

    def open_object(self, item):
        # Открытие объекта/переход в новую папку
        # Обновляем изображение окна
        name_item = self.explorer.item(self.explorer.currentRow(), 0).text()
        type_item = self.explorer.item(self.explorer.currentRow(), 1).text()
        id_item = self.explorer.item(self.explorer.currentRow(), 2).text()

        if type_item == 'Directory':
            self._clients[self._current_address]['id_current_dir'] = id_item
            self.show_current_dir(id_item)
        else:
            self.show_current_file(id_item)

    def show_current_dir(self, id_obj=None):
        # Переходим в директорию
        data = {'address': self.get_current_client_wallet().address}

        if id_obj not in {None, ''}:
            # Передаем id объекта, если создаем новую директорию или открываем файл
            data['id_object'] = id_obj

        response = requests.get(f'http://127.0.0.1:{self._port}/api/get_object', params=data).json()
        self.explorer.clear()
        self.explorer.setRowCount(0)

        for type in ['dirs', 'files']:
            for obj in sorted(response[type], key=lambda k: k['name']):  # Отображаем отсортированные директории и файлы
                row = self.explorer.rowCount()
                self.explorer.setRowCount(row + 1)
                self.explorer.setItem(row, 0, QTableWidgetItem(obj['name']))
                self.explorer.setItem(row, 1, QTableWidgetItem({'dirs': 'Directory', 'files': 'File'}[type]))
                self.explorer.setItem(row, 2, QTableWidgetItem(obj['id_object']))

    def show_current_file(self, id_obj):
        # Открываем файл
        data = {'address': self.get_current_client_wallet().address}
        if id_obj not in {None, ''}:
            # Передаем id объекта, если создаем новую директорию или открываем файл
            data['id_object'] = id_obj

        response = requests.get(f'http://127.0.0.1:{self._port}/api/get_object',
                                params=data)
        # Сохраняем во временные файлы и открываем
        file_name = os.path.join(os.environ['TEMP'], self.explorer.item(self.explorer.currentRow(), 0).text())
        with open(file_name, 'wb') as f:
            [f.write(chunk) for chunk in response.iter_content(SIZE_REPLICA)]

        os.startfile(file_name)

    def create_dir(self):
        # Создание новой директории
        if self._current_address is None:
            QMessageBox.critical(self, "Ошибка", "Нет клиента", QMessageBox.Ok)
        else:
            text, ok = QInputDialog.getText(self, 'Input Dialog',
                                            'Enter name directory:')
            if ok:
                if text == '..':
                    QMessageBox.critical(self, "Ошибка", "Не корректное имя файла", QMessageBox.Ok)
                else:
                    data = {'name': text}
                    id_current_dir = self._clients[self._current_address]['id_current_dir']
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
        # Загрузка нового файла
        if self._current_address is None:
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

                id_current_dir = self._clients[self._current_address]['id_current_dir']
                if id_current_dir:
                    params['id_current_dir'] = id_current_dir

                params = self.signed_data_request(params)

                response = requests.post(f'http://127.0.0.1:{self._port}/api/save_file', params=params,
                                         data=self.chunking(path)).json()
                if 'error' in response:
                    QMessageBox.critical(self, "Error", response['error'], QMessageBox.Ok)
                else:
                    self.show_current_dir(id_current_dir)


def worker_process(cpu, port):
    worker = ClientDCTP('WORKER ' + str(cpu), '127.0.0.1', port)

    @worker.method('add_storage')
    def add_storage(data):
        storage = Storage(worker, data['private_key'])
        storage.start()

    worker.start()


if __name__ == '__main__':

    server = ServerDCTP()


    @server.method('current_state_storage')
    def current_state_storage(data):
        while True:
            try:
                client_manager
                break
            except:
                time.sleep(0.1)

        exist_storage = True
        for i in range(client_manager.list_storages.rowCount()):
            if client_manager.list_storages.item(i, 0).text() == data['id_storage']:
                client_manager.list_storages.setItem(i, 1, QTableWidgetItem(data['state']))
                client_manager.list_storages.hide()
                client_manager.list_storages.show()
                exist_storage = False
                break
        if exist_storage:
            row = client_manager.list_storages.rowCount()
            client_manager.list_storages.setRowCount(row + 1)
            client_manager.list_storages.setSortingEnabled(False)
            client_manager.list_storages.setItem(row, 0, QTableWidgetItem(data['id_storage']))
            client_manager.list_storages.setItem(row, 1, QTableWidgetItem(data['state']))
            client_manager.list_storages.setCurrentCell(row, 0)
            client_manager.list_storages.setSortingEnabled(True)
        print(f'Storage {data["id_storage"]} {data["state"]}')


    server.start()

    for cpu in range(cpu_count()):
        t = Process(target=worker_process, args=[cpu, server.current_port])
        t.start()
    time.sleep(6)
    app = QApplication(sys.argv)
    client_manager = AppClient()
    client_manager.show()
    sys.exit(app.exec_())
