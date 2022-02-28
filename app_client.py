import os
import sys

from PyQt5.QtCore import Qt
import requests
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QDesktopWidget, \
    QInputDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QTabWidget, \
    QFrame, QHBoxLayout, QMenu, QAction, QHeaderView

from fog_nodes_manager import ManagerFogNodes
from utils import get_path, exists_path
from pool import Pool
from wallet import Wallet
from fog_node import SIZE_REPLICA
from client_storage_manager import PORT_DISPATCHER_CLIENT_STORAGE, DispatcherClientStorage


class AppClient(QMainWindow, ManagerFogNodes):
    def __init__(self):
        super().__init__()
        self.pool = None
        self.client_storages = {}
        self._address_pool = None
        self._current_address_client_storage = ''
        self.initUI()
        if exists_path(dirs=['data', 'pool'], file='key'):
            self.start_pool()

    def initUI(self):
        self.geometry = QDesktopWidget().availableGeometry()
        self.setGeometry(1000, 1000, 1000, 800)
        self.move(500, 100)

        # -----------------------------
        # Widgets tab - Client Storages
        # -----------------------------
        tabClientStorages = QFrame()
        layoutClientStorages = QHBoxLayout()

        with open(get_path(dirs=['data', 'client_storage'], file='key'), 'r') as f:
            for key in f.readlines():
                wallet = Wallet(key[:-1])
                if self._current_address_client_storage == '':
                    self._current_address_client_storage = wallet.address
                self.client_storages[wallet.address] = {'wallet': wallet, 'id_current_dir': None}

        self.clientStoragesExplorer = QTableWidget()
        labels = ['Name', 'Type', 'Id']
        self.clientStoragesExplorer.setColumnCount(len(labels))
        self.clientStoragesExplorer.setHorizontalHeaderLabels(labels)
        self.clientStoragesExplorer.verticalHeader().hide()
        self.clientStoragesExplorer.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.clientStoragesExplorer.setShowGrid(False)
        self.clientStoragesExplorer.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.clientStoragesExplorer.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.clientStoragesExplorer.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.clientStoragesExplorer.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.clientStoragesExplorer.setSelectionMode(QAbstractItemView.SingleSelection)
        self.clientStoragesExplorer.itemDoubleClicked.connect(self.open_object)
        if self.client_storages:
            self.show_current_dir(None)

        layoutClientStorages.addWidget(self.clientStoragesExplorer)
        tabClientStorages.setLayout(layoutClientStorages)

        # -----------------------------
        # Widgets tab - Pool
        # -----------------------------
        tabPool = QFrame()
        layoutTabPool = QHBoxLayout()
        tabPool.setLayout(layoutTabPool)

        # -----------------------------
        # Widgets tab - Fog Nodes
        # -----------------------------
        tabFogNodes = QFrame()
        layoutFogNodes = QHBoxLayout()

        self.fogNodesWidget = QTableWidget()
        labels = ['Name', 'State', 'Amount']
        self.fogNodesWidget.setColumnCount(len(labels))
        self.fogNodesWidget.setHorizontalHeaderLabels(labels)
        self.fogNodesWidget.verticalHeader().hide()
        self.fogNodesWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fogNodesWidget.setShowGrid(False)
        self.fogNodesWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fogNodesWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.fogNodesWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fogNodesWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        with open(get_path(dirs=['data', 'fog_nodes'], file='key'), 'r') as f:
            for key in f.readlines():
                wallet = Wallet(key[:-1])
                address = wallet.address
                row = self.fogNodesWidget.rowCount()
                self.fogNodesWidget.setRowCount(row + 1)
                self.fogNodesWidget.setItem(row, 0, QTableWidgetItem(address))
                if address in self.client_storages.keys():
                    self.fogNodesWidget.item(row, 0).setForeground(QColor('green'))
        self.fogNodesWidget.setSortingEnabled(True)
        self.fogNodesWidget.sortByColumn(0, Qt.AscendingOrder)
        self.fogNodesWidget.setCurrentCell(0, 0)
        self.fogNodesWidget.currentCellChanged.connect(self.current_change_client_storage)

        layoutFogNodes.addWidget(self.fogNodesWidget)
        tabFogNodes.setLayout(layoutFogNodes)

        self.tab = QTabWidget()
        self.tab.addTab(tabClientStorages, "Client Storages")
        self.tab.addTab(tabPool, "Pool")
        self.tab.addTab(tabFogNodes, "Fog Nodes")

        self.tab.currentChanged.connect(self._createMenuBar)
        self.setCentralWidget(self.tab)

        self._createActions()
        self._createMenuBar()

        self.setWindowTitle("DeCloud")
        if self._current_address_client_storage:
            self.setWindowTitle("DeCloud  —  " + self._current_address_client_storage)

    def closeEvent(self, event):
        self.showMinimized()
        event.ignore()


    def _createActions(self):
        self.newAction = QAction(self)

        # ---------------
        # Main Action
        # ---------------

        self.exitAction = QAction("Exit", self)
        self.exitAction.triggered.connect(self.close)

        # ---------------
        # Action Client Storages
        # ---------------
        self.createClientStorageAction = QAction("Create client storage", self)
        self.createClientStorageAction.setEnabled(False)
        self.createClientStorageAction.triggered.connect(self.create_client_storage)

        self.sendFileAction = QAction('Send file', self)
        self.sendFileAction.triggered.connect(self.send_file)

        self.createDirAction = QAction("Create directory", self)
        self.createDirAction.triggered.connect(self.create_dir)

        # ---------------
        # Action Pool
        # ---------------

        self.createPoolAction = QAction("Create Pool", self)
        self.createPoolAction.triggered.connect(self.start_pool)

        # ---------------
        # Action Fog Nodes
        # ---------------
        self.createNodeAction = QAction("Create node", self)
        self.createNodeAction.triggered.connect(self.create_node)

    def _createMenuBar(self):
        menuBar = self.menuBar()
        menuBar.clear()

        # ---------------
        # Menu File
        # ---------------
        fileMenu = QMenu("File", self)
        menuBar.addMenu(fileMenu)

        # Client Storages
        if self.tab.currentIndex() == 0:
            self.setWindowTitle("DeCloud  —  " + self._current_address_client_storage)
            clientStoragesMenu = fileMenu.addMenu("Open Storages")
            self.addresses_action = []
            if not self.client_storages:
                clientStoragesMenu.setEnabled(False)

            for name in list(self.client_storages.keys()):
                self.addresses_action.append(QAction(name, self))
                self.addresses_action[-1].triggered.connect(self.change_client_storage_address)
                clientStoragesMenu.addAction(self.addresses_action[-1])

                if self.addresses_action[-1].text() == self._current_address_client_storage:
                    self.addresses_action[-1].setCheckable(True)
                    self.addresses_action[-1].setChecked(True)
                else:
                    self.addresses_action[-1].setCheckable(False)
        # Pool
        elif self.tab.currentIndex() == 1:
            fileMenu.addAction(self.createPoolAction)

            if self._address_pool:
                self.setWindowTitle("DeCloud  —  " + self._address_pool)
                self.createPoolAction.setEnabled(False)
            else:
                self.setWindowTitle("DeCloud")
        # Fog nodes
        elif self.tab.currentIndex() == 2:
            self.setWindowTitle("DeCloud  —  " + self._current_address_client_storage)
            self.fogNodesWidget.setFocus()
            fileMenu.addAction(self.createNodeAction)

        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        # ---------------
        # Menu Edit
        # ---------------
        editMenu = menuBar.addMenu("Edit")

        # Client Storages
        if self.tab.currentIndex() == 0:
            if not self.client_storages:
                editMenu.setEnabled(False)
            editMenu.addAction(self.createDirAction)
            editMenu.addAction(self.sendFileAction)
        # Pool
        elif self.tab.currentIndex() == 1:
            pass
        # Fog nodes
        elif self.tab.currentIndex() == 2:
            editMenu.addAction(self.createClientStorageAction)

        # ---------------
        # Menu Help
        # ---------------
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

    def get_current_client_wallet(self):
        # Получить кошелек
        wallet = self.client_storages[self._current_address_client_storage]['wallet']
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

    def on_change_state(self, data):
        no_exist_node = True
        for i in range(self.fogNodesWidget.rowCount()):
            if self.fogNodesWidget.item(i, 0).text() == data['id_fog_node']:
                self.fogNodesWidget.setItem(i, 1, QTableWidgetItem(data['state']))
                self.fogNodesWidget.hide()
                self.fogNodesWidget.show()
                no_exist_node = False
                break

        if no_exist_node:  # Create new row
            row = self.fogNodesWidget.rowCount()
            self.fogNodesWidget.setRowCount(row + 1)
            self.fogNodesWidget.setSortingEnabled(False)
            self.fogNodesWidget.setItem(row, 0, QTableWidgetItem(data['id_fog_node']))
            self.fogNodesWidget.setItem(row, 1, QTableWidgetItem(data['state']))
            self.fogNodesWidget.setCurrentCell(row, 0)
            self.fogNodesWidget.setSortingEnabled(True)
        print(f'Node {data["id_fog_node"]} {data["state"]}')

    @staticmethod
    def amount_format(amount):
        name_amount_format = ['bEx', 'KbEx', 'MbEx', 'GbEx', 'TbEx', 'PbEx', 'EbEx', 'ZbEx', 'YbEx']
        cut_format = 0
        while amount >= 1024:
            amount /= 1024
            cut_format += 1
        return f'{round(amount, 2)} {name_amount_format[cut_format]}'


    def on_change_balance(self, data):
        for i in range(self.fogNodesWidget.rowCount()):
            if self.fogNodesWidget.item(i, 0).text() == data['id_fog_node']:

                self.fogNodesWidget.setItem(i, 2, QTableWidgetItem(self.amount_format(data['amount'])))
                self.fogNodesWidget.item(i, 2).setTextAlignment(Qt.AlignRight);
                self.fogNodesWidget.hide()
                self.fogNodesWidget.show()
                break

        print(f'Update balance Node {data["id_fog_node"]} {data["amount"]}')

    def start_pool(self):
        try:
            self.pool = Pool()
            self.pool.start()
        except Exception as e:
            print(e)
        self.createPoolAction.setEnabled(False)
        with open(get_path(dirs=['data', 'pool'], file='key'), 'r') as f:
            self._address_pool = Wallet(f.readline()).address

    def current_change_client_storage(self, row):
        self.createClientStorageAction.setEnabled(
            self.fogNodesWidget.item(row, 0).text() not in self.client_storages.keys())

    def change_client_storage_address(self):
        self._current_address_client_storage = self.sender().text()
        [addressAction.setCheckable(False) for addressAction in self.addresses_action]
        self.sender().setCheckable(True)
        self.sender().setChecked(True)
        self.setWindowTitle("DeCloud  —  " + self._current_address_client_storage)
        self.show_current_dir()

    def create_client_storage(self):
        address = self.fogNodesWidget.item(self.fogNodesWidget.currentRow(), 0).text()
        with open(get_path(dirs=['data', 'fog_nodes'], file='key'), 'r') as f:
            for key in f.readlines():
                wallet = Wallet(key[:-1])
                if wallet.address == address:
                    self.client_storages[address] = {'wallet': Wallet(key[:-1]),
                                                     'id_current_dir': None}
                    self.client_storages[address]['wallet'].save_private_key(get_path(dirs=['data', 'client_storage'], file='key'))
                    self.fogNodesWidget.item(self.fogNodesWidget.currentRow(), 0).setForeground(QColor('green'))
                    self.setWindowTitle("DeCloud  —  " + address)
                    self._current_address_client_storage = address
                    self.show_current_dir()
                    self.tab.setCurrentIndex(0)
                    self._createMenuBar()
                    return

    def create_node(self):
        # Создаем новую node
        self.add_fog_node()

    def create_dir(self):
        # Создание новой директории
        if self._current_address_client_storage is None:
            QMessageBox.critical(self, "Ошибка", "Нет клиента", QMessageBox.Ok)
        else:
            text, ok = QInputDialog.getText(self, 'Input Dialog',
                                            'Enter name directory:')
            if ok:
                if text == '..':
                    QMessageBox.critical(self, "Ошибка", "Не корректное имя файла", QMessageBox.Ok)
                else:
                    data = {'name': text}
                    id_current_dir = self.client_storages[self._current_address_client_storage]['id_current_dir']
                    if id_current_dir:
                        data['id_current_dir'] = id_current_dir
                    data = self.signed_data_request(data)

                    response = requests.get(f'http://127.0.0.1:{PORT_DISPATCHER_CLIENT_STORAGE}/api/make_dir',
                                            json=data).json()
                    if 'error' in response:
                        QMessageBox.critical(self, "Error", response['error'], QMessageBox.Ok)
                    else:
                        self.show_current_dir(id_current_dir)

    def send_file(self):
        # Загрузка нового файла
        if self._current_address_client_storage is None:
            QMessageBox.critical(self, "Ошибка", "Нет клиента", QMessageBox.Ok)
        else:
            path = QFileDialog.getOpenFileName(self, "Select a file...", None, filter="All files (*)")[0]
            if path != "":
                file_name = path.split('/')[-1]
                for i in range(self.clientStoragesExplorer.rowCount()):
                    if self.clientStoragesExplorer.item(i, 0).text() == file_name and self.clientStoragesExplorer.item(
                            i, 1).text() == 'File':
                        QMessageBox.critical(self, "Ошибка", "Такое имя файла уже существует", QMessageBox.Ok)
                        return

                print(f'Загружаем файл {file_name}')
                params = {'file_name': file_name}

                id_current_dir = self.client_storages[self._current_address_client_storage]['id_current_dir']
                if id_current_dir:
                    params['id_current_dir'] = id_current_dir

                params = self.signed_data_request(params)
                response = requests.post(f'http://127.0.0.1:{PORT_DISPATCHER_CLIENT_STORAGE}/api/save_file',
                                         params=params,
                                         data=self.chunking(path)).json()
                if 'error' in response:
                    QMessageBox.critical(self, "Error", response['error'], QMessageBox.Ok)
                else:
                    self.show_current_dir(id_current_dir)



    def open_object(self, item):
        # Открытие объекта/переход в новую папку
        # Обновляем изображение окна
        name_item = self.clientStoragesExplorer.item(self.clientStoragesExplorer.currentRow(), 0).text()
        type_item = self.clientStoragesExplorer.item(self.clientStoragesExplorer.currentRow(), 1).text()
        id_item = self.clientStoragesExplorer.item(self.clientStoragesExplorer.currentRow(), 2).text()

        if type_item == 'Directory':
            self.client_storages[self._current_address_client_storage]['id_current_dir'] = id_item
            self.show_current_dir(id_item)
        else:
            self.show_current_file(id_item)

    def show_current_dir(self, id_obj=None):
        # Переходим в директорию
        data = {'address': self.get_current_client_wallet().address}

        if id_obj not in {None, ''}:
            # Передаем id объекта, если создаем новую директорию или открываем файл
            data['id_object'] = id_obj
        while True:
            try:
                response = requests.get(f'http://127.0.0.1:{PORT_DISPATCHER_CLIENT_STORAGE}/api/get_object', params=data).json()
                break
            except:
                pass

        self.clientStoragesExplorer.clear()
        self.clientStoragesExplorer.setRowCount(0)

        for type in ['dirs', 'files']:
            for obj in sorted(response[type], key=lambda k: k['name']):  # Отображаем отсортированные директории и файлы
                row = self.clientStoragesExplorer.rowCount()
                self.clientStoragesExplorer.setRowCount(row + 1)
                self.clientStoragesExplorer.setItem(row, 0, QTableWidgetItem(obj['name']))
                self.clientStoragesExplorer.setItem(row, 1,
                                                    QTableWidgetItem({'dirs': 'Directory', 'files': 'File'}[type]))
                self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(obj['id_object']))

    def show_current_file(self, id_obj):
        # Открываем файл
        data = {'address': self.get_current_client_wallet().address}
        if id_obj not in {None, ''}:
            # Передаем id объекта, если создаем новую директорию или открываем файл
            data['id_object'] = id_obj

        response = requests.get(f'http://127.0.0.1:{PORT_DISPATCHER_CLIENT_STORAGE}/api/get_object',
                                params=data)
        # Сохраняем во временные файлы и открываем
        file_name = os.path.join(os.environ['TEMP'],
                                 self.clientStoragesExplorer.item(self.clientStoragesExplorer.currentRow(), 0).text())
        with open(file_name, 'wb') as f:
            [f.write(chunk) for chunk in response.iter_content(SIZE_REPLICA)]

        os.startfile(file_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dispatcher = DispatcherClientStorage(PORT_DISPATCHER_CLIENT_STORAGE)
    dispatcher.start()

    client_manager = AppClient()
    client_manager.show()
    sys.exit(app.exec_())
