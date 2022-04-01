import functools
from datetime import datetime
import json
import os
import time
from threading import Thread

import requests
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QGuiApplication
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem, QAction, \
    QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QDialog, QLineEdit, QMessageBox, QMenu, QInputDialog, QFileDialog
from _pysha3 import sha3_256

from fog_node import SIZE_REPLICA
from fog_nodes_manager import ManagerFogNodes
from pool import Pool
from utils import LoadJsonFile, amount_format
from wallet import Wallet
from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME, POOL_BACKGROUND_COLOR, CLIENT_STORAGE_FOREGROUND_COLOR, \
    BACKGROUND_COLOR


class ClientStoragesExplorer(QTableWidget):
    update_dir = pyqtSignal(dict)
    message = pyqtSignal(str)

    def __init__(self, address=''):
        super().__init__()
        self._current_id = ''
        self._address = address
        self._last_response_hash = ''
        self.clipboard = QGuiApplication.clipboard()

        labels = ['Id', 'Name', 'Date', 'Type', 'Size']
        self.setColumnCount(len(labels))
        self.setHorizontalHeaderLabels(labels)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.setColumnHidden(0, True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.itemDoubleClicked.connect(self.open_object)

        update_data_thread = Thread(target=self.update_data)
        update_data_thread.start()

    def get_path(self):
        return self._address + '/' + self._current_id

    @property
    def current_id_dir(self):
        return self._current_id

    @current_id_dir.setter
    def current_id_dir(self, current_id):
        self._current_id = current_id

    def change_path(self, path):
        if '/' in path:
            self._address, self._current_id = path.split('/')[:2]
        else:
            self._address = path
            self._current_id = ''
        if self._address == '':
            self.update_dir.emit({})
        else:
            self.show_current_object()

    def change_address(self, address):
        self._address = address

    def open_object(self, item):
        # Открытие объекта/переход в новую папку
        # Обновляем изображение окна
        id_item = self.item(self.currentRow(), 0).text()
        self._current_id = id_item
        self.show_current_object()

    def show_current_object(self):
        try:
            response = requests.get(
                f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_object/{self._address}',
                params={'id_object': self._current_id})
        except:
            self.message.emit('no connection')
            return
        try:
            response = response.json()
            type_object = 'dir'
        except:
            type_object = 'file'

        if type_object == 'dir':
            if 'error' in response:
                self.message.emit(response['error'])
                return
            if sha3_256(bytes(json.dumps(response), 'utf-8')).hexdigest() == self._last_response_hash:
                return
            self._last_response_hash = sha3_256(bytes(json.dumps(response), 'utf-8')).hexdigest()
            self.update_dir.emit(response['json'])
        elif type_object == 'file':
            # Сохраняем во временные файлы и открываем
            try:
                info_object = requests.get(
                    f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_info_object/{self._address}',
                    params={'id_object': self._current_id}).json()
            except:
                self.message.emit('no connection')
                return
            file_name = os.path.join(os.environ['TEMP'], info_object['name'])
            with open(file_name, 'wb') as f:
                [f.write(chunk) for chunk in response.iter_content(SIZE_REPLICA)]
            os.startfile(file_name)
            if self._current_id != self.item(self.currentRow(), 0).text():
                self.message.emit('ok')

    def update_data(self):
        while True:
            time.sleep(15)
            try:
                if self._address != '':
                    info_object = requests.get(
                        f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_info_object/{self._address}',
                        params={'id_object': self._current_id}).json()
                    if 'error' not in info_object and info_object['type'] == 'dir':
                        self.show_current_object()
            except:
                self.message.emit('no connection')

    def copy_path(self):
        self.clipboard.setText(self._address + '/' + self.item(self.currentRow(), 0).text())


class ClientStorageWidget(QVBoxLayout):
    change_ns = pyqtSignal(str, str)

    def __init__(self, address: str):
        super().__init__()
        self._address = address
        self._address_normal = None
        self._wallet = None
        for key in LoadJsonFile('data/clients_manager/key').as_list():
            if Wallet(key).address == address:
                self._wallet = Wallet(key)
                break
        self._full_amount = 0
        self._occupied_amount = 0
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.createDirectory = QPushButton("Create directory")
        self.createDirectory.clicked.connect(self.create_dir)

        self.createSendFile = QPushButton("Send file")
        self.createSendFile.clicked.connect(self.send_file)

        self.sendRegistrationDomainName = QPushButton("Registration domain name")
        self.sendRegistrationDomainName.clicked.connect(self.registration_domain_name)

        self.sendByteExButton = QPushButton("Send Bytes")
        self.sendByteExButton.clicked.connect(self.send_byteEx)

        layout_v = QVBoxLayout()
        layoutAllBalance = QHBoxLayout()
        self.labelAllBalanceClient = QLabel('Полный баланс: ')
        self.labelAmountClient = QLabel()
        layoutAllBalance.addWidget(self.labelAllBalanceClient)
        layoutAllBalance.addWidget(self.labelAmountClient)
        layout_v.addLayout(layoutAllBalance)

        layoutOccupiedBalance = QHBoxLayout()
        self.labelOccupiedBalance = QLabel('Использовано: ')
        self.labelOccupiedAmount = QLabel(amount_format(0))
        layoutOccupiedBalance.addWidget(self.labelOccupiedBalance)
        layoutOccupiedBalance.addWidget(self.labelOccupiedAmount)
        layout_v.addLayout(layoutOccupiedBalance)

        layout.addWidget(self.createDirectory)
        layout.addWidget(self.createSendFile)
        layout.addWidget(self.sendRegistrationDomainName)
        layout.addWidget(self.sendByteExButton)
        layout.addStretch(1)
        layout.addLayout(layout_v)
        self.addLayout(layout)

        self.label_message = QLabel()
        self.label_message.hide()
        self.addWidget(self.label_message)

        self.clientStoragesExplorer = ClientStoragesExplorer(self._address)
        self.clientStoragesExplorer.update_dir.connect(self.update_dir)
        self.clientStoragesExplorer.message.connect(self.message_explorer)
        self.clientStoragesExplorer.change_path(self._address)
        self.clientStoragesExplorer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.clientStoragesExplorer.customContextMenuRequested.connect(self.context_menu_open)
        self.addWidget(self.clientStoragesExplorer)

    def message_explorer(self, text):
        if text == 'ok':
            self.label_message.hide()
            self.clientStoragesExplorer.show()
        else:
            self.clientStoragesExplorer.hide()
            self.label_message.setText(text)
            self.label_message.show()

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

    def context_menu_open(self, position):
        context_menu = QMenu(self.clientStoragesExplorer)

        if self.clientStoragesExplorer.itemAt(position):
            copyAction = QAction('Copy Path')
            copyAction.triggered.connect(self.clientStoragesExplorer.copy_path)
            context_menu.addAction(copyAction)
        try:
            response = requests.get(
                f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_all_ns/{self._address}').json()
            self._address_normal = list(response)[0]
            if response[self._address_normal]:
                useNs_menu = QMenu('Use ns')
                context_menu.addMenu(useNs_menu)
                self.ns_actions = []
                if self._address != self._address_normal:
                    self.ns_actions = [QAction(self._address_normal)]
                    self.ns_actions[0].triggered.connect(self.use_ns)
                    useNs_menu.addAction(self.ns_actions[0])
                    useNs_menu.addSeparator()

                for ns in response[self._address_normal]:
                    if self._address != ns:
                        self.ns_actions.append(QAction(ns))
                        self.ns_actions[-1].triggered.connect(self.use_ns)
                        useNs_menu.addAction(self.ns_actions[-1])
        except:
            pass

        context_menu.exec_(self.clientStoragesExplorer.viewport().mapToGlobal(position))
        self.ns_actions = None

    def use_ns(self):
        self._address = self.sender().text()
        self.change_ns.emit(self._address, self._address_normal)

    def update_dir(self, data):
        if not data:
            self.clientStoragesExplorer.setRowCount(0)
            return
        self.clientStoragesExplorer.show()
        self.label_message.hide()
        self._occupied_amount = data['occupied']
        self.labelOccupiedAmount.setText(amount_format(self._occupied_amount))
        self.clientStoragesExplorer.setRowCount(sum([(len(data[type])) for type in ['dirs', 'files']]))
        row = 0
        for type in ['dirs', 'files']:
            for obj in sorted(data[type], key=lambda k: k['name']):  # Отображаем отсортированные директории и файлы
                self.clientStoragesExplorer.setItem(row, 0, QTableWidgetItem(obj['id_object']))
                self.clientStoragesExplorer.setItem(row, 1, QTableWidgetItem(obj['name']))
                self.clientStoragesExplorer.setItem(row, 3,
                                                    QTableWidgetItem({'dirs': 'Directory', 'files': 'File'}[type]))
                if 'info' in obj.keys() and obj['info']:
                    self.clientStoragesExplorer.item(row, 1).setForeground(QColor(CLIENT_STORAGE_FOREGROUND_COLOR))
                    date = datetime.fromtimestamp(obj['info']['date']).strftime('%Y-%m-%d %H:%M:%S')
                    self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(date))
                    self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(amount_format(obj['info']['size'])))
                elif obj['name'] == '..':
                    self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(''))
                    self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(''))
                else:
                    self.clientStoragesExplorer.item(row, 1).setForeground(QColor('red'))
                    date = datetime.fromtimestamp(datetime.utcnow().timestamp()).strftime('%Y-%m-%d %H:%M:%S')
                    self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(date))
                    if type == 'dirs':
                        self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(amount_format(0)))
                    else:
                        self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(amount_format(0)))
                row += 1

    def signed_data_request(self, data=None):
        # Формируем request и подписываем
        if data is None:
            data = {}
        data['public_key'] = self._wallet.public_key
        data['address'] = self._wallet.address
        data['sign'] = self._wallet.sign(data)

        return data

    def registration_domain_name(self):
        name, ok = QInputDialog.getText(self.clientStoragesExplorer, 'Registration domain name', 'Add domain name:')
        if ok:
            try:
                data = {'address': self._address, 'name': name}
                requests.post(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/registration_domain_name',
                              json=data)
            except:
                pass

    def change_balance(self, amount):
        self._full_amount = amount
        self.labelAmountClient.setText(amount_format(amount))

    def send_byteEx(self):
        Send_ByteEx(self._address).exec()

    def create_dir(self):
        text, ok = QInputDialog.getText(self.clientStoragesExplorer, 'Input Dialog', 'Enter name directory:')
        if ok:
            if text == '..':
                QMessageBox.critical(self.clientStoragesExplorer, "Error", "Не корректное имя файла", QMessageBox.Ok)
            else:
                if 400 + self._occupied_amount > self._full_amount:
                    QMessageBox.critical(self.clientStoragesExplorer, "Error", "Не хватает места", QMessageBox.Ok)
                    return
                data = {'name': text}
                id_current_dir = self.clientStoragesExplorer.current_id_dir
                if id_current_dir:
                    data['id_current_dir'] = id_current_dir
                data = self.signed_data_request(data)
                response = requests.get(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/make_dir',
                                        json=data).json()
                if 'error' in response:
                    QMessageBox.critical(self.clientStoragesExplorer, "Error", response['error'], QMessageBox.Ok)
                else:
                    self.clientStoragesExplorer.current_id_dir = id_current_dir
                    self.clientStoragesExplorer.show_current_object()

    def send_file(self):
        # Загрузка нового файла
        path = \
            QFileDialog.getOpenFileName(self.clientStoragesExplorer, "Select a file...", None, filter="All files (*)")[
                0]
        if path != "":
            if os.path.getsize(path) + self._occupied_amount > self._full_amount:
                QMessageBox.critical(self.clientStoragesExplorer, "Error", "Не хватает места", QMessageBox.Ok)
                return
            file_name = path.split('/')[-1]
            for i in range(self.clientStoragesExplorer.rowCount()):
                if self.clientStoragesExplorer.item(i, 1).text() == file_name and self.clientStoragesExplorer.item(
                        i, 3).text() == 'File':
                    QMessageBox.critical(self.clientStoragesExplorer, "Error", "Такое имя файла уже существует",
                                         QMessageBox.Ok)
                    return

            print(f'Загружаем файл {file_name}')
            params = {'file_name': file_name}

            id_current_dir = self.clientStoragesExplorer.current_id_dir
            if id_current_dir:
                params['id_current_dir'] = id_current_dir

            params = self.signed_data_request(params)
            response = requests.post(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/save_file',
                                     params=params,
                                     data=self.chunking(path)).json()
            if 'error' in response:
                QMessageBox.critical(self.clientStoragesExplorer, "Error", response['error'], QMessageBox.Ok)
            else:
                self.clientStoragesExplorer.current_id_dir = id_current_dir
                self.clientStoragesExplorer.show_current_object()


class PoolWidget(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self._address_pool = None
        self.pool_balance = 0
        self._is_run = False
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.sendByteExButton = QPushButton("Send Bytes")
        self.sendByteExButton.clicked.connect(self.send_byteEx)

        layoutAllBalancePool = QHBoxLayout()
        self.labelAllBalancePool = QLabel('Полный баланс: ')
        self.labelAmountPool = QLabel(amount_format(0))
        layoutAllBalancePool.addStretch(1)
        layoutAllBalancePool.addWidget(self.labelAllBalancePool)
        layoutAllBalancePool.addWidget(self.labelAmountPool)

        layout.addWidget(self.sendByteExButton)
        layout.addStretch(1)
        layout.addLayout(layoutAllBalancePool)
        self.addLayout(layout)

        self.infoBlockchain = QTableWidget()
        labels = ['number block', 'recipient pool', 'amount pool', 'recipient fog node', 'amount fog node',
                  'transactions']
        self.infoBlockchain.setColumnCount(len(labels))
        self.infoBlockchain.setHorizontalHeaderLabels(labels)
        self.infoBlockchain.verticalHeader().hide()
        self.infoBlockchain.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.infoBlockchain.setShowGrid(False)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.infoBlockchain.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.infoBlockchain.setSelectionMode(QAbstractItemView.SingleSelection)

        self.addWidget(self.infoBlockchain)

        private_key = LoadJsonFile('data/pool/key').as_string()
        if private_key:
            self.start_pool(private_key)

    def is_run(self):
        return self._is_run

    def send_byteEx(self):
        Send_ByteEx(self._address_pool).exec()

    def start_pool(self, private_key):
        try:
            self.pool = Pool(private_key)
            self.pool.start()
            self._address_pool = Wallet(private_key).address
            self._is_run = True
        except Exception as e:
            print(e)

    def change_balance_pool(self, amount):
        self.pool_balance = amount
        self.labelAmountPool.setText(amount_format(amount))


class FogNodesWidget(QHBoxLayout):
    createPool = pyqtSignal(str)
    changeBalanceClientsStorage = pyqtSignal(str, int)
    createClientStorage = pyqtSignal(str)
    changeBalancePool = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.clipboard = QGuiApplication.clipboard()
        self.initUI()

    def initUI(self):
        labels = ['Name', 'State', 'Amount', 'Full amount', 'Normal Address']
        self.fogNodesTableWidget = QTableWidget()
        self.fogNodesTableWidget.setColumnCount(len(labels))
        self.fogNodesTableWidget.setHorizontalHeaderLabels(labels)
        self.fogNodesTableWidget.verticalHeader().hide()
        self.fogNodesTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fogNodesTableWidget.setShowGrid(False)
        self.fogNodesTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fogNodesTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.fogNodesTableWidget.setColumnHidden(3, True)
        self.fogNodesTableWidget.setColumnHidden(4, True)
        self.fogNodesTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fogNodesTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        private_key_pool = LoadJsonFile('data/pool/key').as_string()
        if private_key_pool:
            self.address_pool = Wallet(private_key_pool).address
        else:
            self.address_pool = ''
        clients_address = [Wallet(key).address for key in LoadJsonFile('data/clients_manager/key').as_list()]
        for key in LoadJsonFile('data/fog_nodes/key').as_list():
            wallet = Wallet(key)
            address = wallet.address
            row = self.fogNodesTableWidget.rowCount()
            self.fogNodesTableWidget.setRowCount(row + 1)
            self.fogNodesTableWidget.setItem(row, 0, QTableWidgetItem(address))
            self.fogNodesTableWidget.setItem(row, 4, QTableWidgetItem(address))
            if address in clients_address:
                self.fogNodesTableWidget.item(row, 0).setForeground(QColor(CLIENT_STORAGE_FOREGROUND_COLOR))
            if self.address_pool == address:
                self.fogNodesTableWidget.item(row, 0).setBackground(QColor(POOL_BACKGROUND_COLOR))

        self.fogNodesTableWidget.setSortingEnabled(True)
        self.fogNodesTableWidget.sortByColumn(0, Qt.AscendingOrder)
        self.fogNodesTableWidget.setCurrentCell(0, 0)

        self.fogNodesTableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fogNodesTableWidget.customContextMenuRequested.connect(self.fog_node_context_menu_open)
        self.fogNodesTableWidget.cellClicked.connect(self.current_item_change)
        self.mfn = ManagerFogNodes()
        self.mfn.load_fog_nodes('data/fog_nodes/key')
        self.mfn.on_change_balance = self.on_change_balance
        self.mfn.on_change_state = self.on_change_state
        layout = QVBoxLayout()
        self.createNodeButton = QPushButton("Create Fog_Node")
        self.createNodeButton.clicked.connect(self.create_node)
        self.create_and_open_PoolButton = QPushButton("Create Pool")
        self.create_and_open_PoolButton.clicked.connect(self.create_and_open_pool)
        self.sendByteExButton = QPushButton("Send Bytes")
        self.sendByteExButton.clicked.connect(self.send_byteEx)
        self.create_and_open_client_storageButton = QPushButton("Create Client Storage")
        self.create_and_open_client_storageButton.clicked.connect(self.create_client_storage)
        self.create_and_open_client_storageButton.setVisible(self.fogNodesTableWidget.rowCount() > 0)
        self.create_and_open_PoolButton.setVisible(not self.address_pool and self.fogNodesTableWidget.rowCount() > 0)
        layout.addWidget(self.createNodeButton)
        layout.addWidget(self.create_and_open_PoolButton)
        layout.addWidget(self.create_and_open_client_storageButton)
        layout.addWidget(self.sendByteExButton)
        layout.addStretch(1)
        self.addWidget(self.fogNodesTableWidget)
        self.addLayout(layout)

    def current_item_change(self, row, column):
        self.create_and_open_PoolButton.setVisible(
            not bool(self.address_pool) and self.fogNodesTableWidget.rowCount() > 0 or
            self.fogNodesTableWidget.item(row, 0).background().color().name() == POOL_BACKGROUND_COLOR)
        if self.fogNodesTableWidget.item(row, 0).foreground().color().name() == CLIENT_STORAGE_FOREGROUND_COLOR:
            self.create_and_open_client_storageButton.setText("Open Client Storage")
        else:
            self.create_and_open_client_storageButton.setText("Create Client Storage")

    def create_and_open_pool(self):
        address = self.current_fog_node()
        for item in LoadJsonFile('data/fog_nodes/key').as_list():
            if Wallet(item).address == address:
                self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).setBackground(
                    QColor(POOL_BACKGROUND_COLOR))
                self.address_pool = address
                self.create_and_open_PoolButton.setText('Open Pool')
                self.createPool.emit(item)
                break

    def current_fog_node(self):
        if self.fogNodesTableWidget.rowCount() > 0:
            return self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).text()
        return ""

    def send_byteEx(self):
        Send_ByteEx(self.current_fog_node()).exec()

    def _copy_fog_node_address(self):
        self.clipboard.setText(self.current_fog_node())

    def create_node(self):
        # Создаем новую node
        self.mfn.add_fog_node()
        self.create_and_open_PoolButton.setVisible(not self.address_pool)
        self.create_and_open_client_storageButton.setVisible(True)

    def on_change_balance(self, data):
        for i in range(self.fogNodesTableWidget.rowCount()):
            if self.fogNodesTableWidget.item(i, 4).text() == data['id_fog_node']:
                self.fogNodesTableWidget.setItem(i, 2, QTableWidgetItem(amount_format(data['amount'])))
                self.fogNodesTableWidget.setItem(i, 3, QTableWidgetItem(str(data['amount'])))
                self.fogNodesTableWidget.item(i, 2).setTextAlignment(Qt.AlignRight)
                if self.fogNodesTableWidget.item(i, 4).text() == self.address_pool:
                    self.changeBalancePool.emit(data['amount'])
                self.changeBalanceClientsStorage.emit(self.fogNodesTableWidget.item(i, 0).text(), data['amount'])
                self.fogNodesTableWidget.hide()
                self.fogNodesTableWidget.show()
                return

    def on_change_state(self, data):
        no_exist_node = True
        for i in range(self.fogNodesTableWidget.rowCount()):
            if self.fogNodesTableWidget.item(i, 4).text() == data['id_fog_node']:
                self.fogNodesTableWidget.setItem(i, 1, QTableWidgetItem(data['state']))
                self.fogNodesTableWidget.hide()
                self.fogNodesTableWidget.show()
                no_exist_node = False
                break

        if no_exist_node:  # Create new row
            row = self.fogNodesTableWidget.rowCount()
            self.fogNodesTableWidget.setRowCount(row + 1)
            self.fogNodesTableWidget.setSortingEnabled(False)
            self.fogNodesTableWidget.setItem(row, 0, QTableWidgetItem(data['id_fog_node']))
            self.fogNodesTableWidget.item(row, 0).setBackground(QColor(BACKGROUND_COLOR))
            self.fogNodesTableWidget.setItem(row, 4, QTableWidgetItem(data['id_fog_node']))
            self.fogNodesTableWidget.setItem(row, 1, QTableWidgetItem(data['state']))
            self.fogNodesTableWidget.setItem(row, 3, QTableWidgetItem('0'))
            self.fogNodesTableWidget.setCurrentCell(row, 0)
            self.fogNodesTableWidget.setSortingEnabled(True)
        print(f'Node {data["id_fog_node"]} {data["state"]}')

    def fog_node_context_menu_open(self, position):
        if self.fogNodesTableWidget.itemAt(position):
            context_menu = QMenu(self.fogNodesTableWidget)
            copyFogNodeAction = QAction('Copy address', self)
            copyFogNodeAction.triggered.connect(self._copy_fog_node_address)
            context_menu.addAction(copyFogNodeAction)
            context_menu.exec_(self.fogNodesTableWidget.viewport().mapToGlobal(position))

    def create_client_storage(self):
        self.createClientStorage.emit(self.current_fog_node())
        self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).setForeground(
            QColor(CLIENT_STORAGE_FOREGROUND_COLOR))


class Send_ByteEx(QDialog):
    def __init__(self, sender: str):
        super().__init__()

        from PyQt5.QtGui import QIntValidator
        from PyQt5.QtWidgets import QGridLayout, QDialogButtonBox
        self.resize(500, 200)
        layoutv = QVBoxLayout()

        grid = QGridLayout()
        grid.setSpacing(10)

        textSender = QLabel('Sender: ')
        self.lineEditSender = QLineEdit(sender)
        grid.addWidget(textSender, 1, 0)
        grid.addWidget(self.lineEditSender, 1, 1)

        textOwner = QLabel('Owner: ')
        self.lineEditOwner = QLineEdit()
        grid.addWidget(textOwner, 2, 0)
        grid.addWidget(self.lineEditOwner, 2, 1)

        textAmount = QLabel('Amount ByteEx: ')
        self.lineEditAmount = QLineEdit()
        self.lineEditAmount.setValidator(QIntValidator(0, 100000, self))
        grid.addWidget(textAmount, 3, 0)
        grid.addWidget(self.lineEditAmount, 3, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.send_request)
        button_box.rejected.connect(self.reject)

        layoutv.addLayout(grid)
        layoutv.addStretch(1)
        layoutv.addWidget(button_box)

        self.setLayout(layoutv)
        self.setWindowTitle("Send ByteEx")

    def send_request(self):
        try:
            response = requests.get(
                f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_free_balance/{self.lineEditSender.text()}').json()
        except:
            QMessageBox.critical(self, "Error", 'Error connection', QMessageBox.Ok)
            return
        if response['status'] == 100:
            QMessageBox.critical(self, "Error", response['status_text'], QMessageBox.Ok)
            return

        if self.lineEditAmount.text() == '':
            self.lineEditAmount.setText('0')
        amount = int(self.lineEditAmount.text())
        if amount <= response['amount_free_balance']:
            transaction = {'sender': self.lineEditSender.text(), 'owner': self.lineEditOwner.text(),
                           'count': amount}
            try:
                response = requests.post(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/new_transaction',
                                         json=transaction)
            except:
                pass

            if response.status_code == 404:
                QMessageBox.critical(self, "Error", 'Error connection', QMessageBox.Ok)
            elif response.json()['status'] == 100:
                QMessageBox.critical(self, "Error", response.json()['status_text'], QMessageBox.Ok)
            else:
                self.accept()
        else:
            QMessageBox.critical(self, "Error", f"{self.lineEditOwner.text()} don't have enough byteEx", QMessageBox.Ok)


class SearchClientStorage(QVBoxLayout):
    change_search_state = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.search = QLineEdit()
        layout.addWidget(self.search, stretch=5)
        self.searchButton = QPushButton('Search')
        layout.addWidget(self.searchButton)
        self.addLayout(layout)
        self.searchButton.clicked.connect(self.open_client_storage)

        self.label_message = QLabel()
        self.label_message.hide()
        self.addWidget(self.label_message)

        self.clientStoragesExplorer = ClientStoragesExplorer()
        self.clientStoragesExplorer.update_dir.connect(self.update_dir)
        self.clientStoragesExplorer.message.connect(self.message_explorer)
        self.clientStoragesExplorer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.clientStoragesExplorer.customContextMenuRequested.connect(self.context_menu_open)
        self.addWidget(self.clientStoragesExplorer)

    def open_client_storage(self):
        path = self.search.text()

        if path != self.clientStoragesExplorer.get_path():
            self.change_search_state.emit(path)
        self.clientStoragesExplorer.change_path(path)

    def update_dir(self, data):
        if not data:
            self.clientStoragesExplorer.setRowCount(0)
            return
        self.search.setText(data['address'] + '/' + data['id_object'])
        self.clientStoragesExplorer.setRowCount(sum([(len(data[type])) for type in ['dirs', 'files']]))
        row = 0
        for type in ['dirs', 'files']:
            for obj in sorted(data[type], key=lambda k: k['name']):  # Отображаем отсортированные директории и файлы
                self.clientStoragesExplorer.setItem(row, 0, QTableWidgetItem(obj['id_object']))
                self.clientStoragesExplorer.setItem(row, 1, QTableWidgetItem(obj['name']))
                self.clientStoragesExplorer.setItem(row, 3,
                                                    QTableWidgetItem({'dirs': 'Directory', 'files': 'File'}[type]))
                if 'info' in obj.keys() and obj['info']:
                    date = datetime.fromtimestamp(obj['info']['date']).strftime('%Y-%m-%d %H:%M:%S')
                    self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(date))
                    self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(amount_format(obj['info']['size'])))
                elif obj['name'] == '..':
                    self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(''))
                    self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(''))
                row += 1
        self.clientStoragesExplorer.show()
        self.label_message.hide()

    def context_menu_open(self, position):
        if self.clientStoragesExplorer.itemAt(position):
            context_menu = QMenu(self.clientStoragesExplorer)
            copyAction = QAction('Copy Path')
            copyAction.triggered.connect(self.clientStoragesExplorer.copy_path)
            context_menu.addAction(copyAction)
            context_menu.exec_(self.clientStoragesExplorer.viewport().mapToGlobal(position))

    def message_explorer(self, text):
        if text == 'ok':
            self.label_message.setText('')
            self.label_message.show()
            self.clientStoragesExplorer.hide()
        else:
            self.clientStoragesExplorer.hide()
            self.label_message.setText(text)
            self.label_message.show()
