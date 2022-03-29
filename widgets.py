from datetime import datetime
import json
import os
import time
from threading import Thread

import requests
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QGuiApplication
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem, QAction, \
    QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QDialog, QLineEdit, QMessageBox, QMenu, QInputDialog, QFileDialog
from _pysha3 import sha3_256

from fog_node import SIZE_REPLICA
from fog_nodes_manager import ManagerFogNodes
from pool import Pool
from utils import SaveJsonFile, LoadJsonFile, amount_format
from wallet import Wallet
from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME, POOL_BACKGROUND_COLOR, CLIENT_STORAGE_FOREGROUND_COLOR


class ClientStorageWidget(QVBoxLayout):
    def __init__(self, address: str):
        super().__init__()
        self._address = address
        self._wallet = None
        for key in LoadJsonFile('data/clients_manager/key').as_list():
            if Wallet(key).address == address:
                self._wallet = Wallet(key)
                break
        self.current_id_dir = None
        self._full_amount = 0
        self.occupied_amount = 0
        self.last_response_hash = 0
        self.initUI()

        update_data_thread = Thread(target=self.update_data)
        update_data_thread.start()

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


        self.clientStoragesExplorer = QTableWidget()
        labels = ['Id', 'Name', 'Date', 'Type', 'Size']
        self.clientStoragesExplorer.setColumnCount(len(labels))
        self.clientStoragesExplorer.setHorizontalHeaderLabels(labels)
        self.clientStoragesExplorer.verticalHeader().hide()
        self.clientStoragesExplorer.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.clientStoragesExplorer.setShowGrid(False)
        self.clientStoragesExplorer.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.clientStoragesExplorer.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.clientStoragesExplorer.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.clientStoragesExplorer.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.clientStoragesExplorer.setColumnHidden(0, True)
        self.clientStoragesExplorer.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.clientStoragesExplorer.setSelectionMode(QAbstractItemView.SingleSelection)
        self.clientStoragesExplorer.itemDoubleClicked.connect(self.open_object)

        self.addWidget(self.clientStoragesExplorer)

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
                data = {'address': self._address,
                        'name': name}
                response = requests.post(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/'
                                         f'api/registration_domain_name',
                                         json=data)
            except:
                pass

    def update_data(self):
        while True:
            self.show_current_dir()
            time.sleep(15)

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
                if 400 + self.occupied_amount > self._full_amount:
                    QMessageBox.critical(self.clientStoragesExplorer, "Error", "Не хватает места", QMessageBox.Ok)
                    return
                data = {'name': text}
                id_current_dir = self.current_id_dir
                if id_current_dir:
                    data['id_current_dir'] = id_current_dir
                data = self.signed_data_request(data)
                response = requests.get(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/make_dir',
                                        json=data).json()
                if 'error' in response:
                    QMessageBox.critical(self.clientStoragesExplorer, "Error", response['error'], QMessageBox.Ok)
                else:
                    self.current_id_dir = id_current_dir
                    self.show_current_dir()

    def send_file(self):
        # Загрузка нового файла
        path = QFileDialog.getOpenFileName(self.clientStoragesExplorer, "Select a file...", None, filter="All files (*)")[0]
        if path != "":
            if os.path.getsize(path) + self.occupied_amount > self._full_amount:
                QMessageBox.critical(self.clientStoragesExplorer, "Error", "Не хватает места", QMessageBox.Ok)
                return
            file_name = path.split('/')[-1]
            for i in range(self.clientStoragesExplorer.rowCount()):
                if self.clientStoragesExplorer.item(i, 1).text() == file_name and self.clientStoragesExplorer.item(
                        i, 3).text() == 'File':
                    QMessageBox.critical(self.clientStoragesExplorer, "Error", "Такое имя файла уже существует", QMessageBox.Ok)
                    return

            print(f'Загружаем файл {file_name}')
            params = {'file_name': file_name}

            id_current_dir = self.current_id_dir
            if id_current_dir:
                params['id_current_dir'] = id_current_dir

            params = self.signed_data_request(params)
            response = requests.post(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/save_file',
                                     params=params,
                                     data=self.chunking(path)).json()
            if 'error' in response:
                QMessageBox.critical(self.clientStoragesExplorer, "Error", response['error'], QMessageBox.Ok)
            else:
                self.current_id_dir = id_current_dir
                self.show_current_dir()

    def open_object(self, item):
        # Открытие объекта/переход в новую папку
        # Обновляем изображение окна
        id_item = self.clientStoragesExplorer.item(self.clientStoragesExplorer.currentRow(), 0).text()
        type_item = self.clientStoragesExplorer.item(self.clientStoragesExplorer.currentRow(), 3).text()

        if type_item == 'Directory':
            self.current_id_dir = id_item
            self.show_current_dir()
        else:
            self.show_current_file(id_item)

    def show_current_dir(self):
        # Переходим в директорию
        data = {'address': self._address}

        if self.current_id_dir not in {None, ''}:
            # Передаем id объекта, если создаем новую директорию или открываем файл
            data['id_object'] = self.current_id_dir
        while True:
            try:
                response = requests.get(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_object',
                                        params=data).json()
                break
            except:
                time.sleep(0.1)

        if sha3_256(bytes(json.dumps(response), 'utf-8')).digest() == self.last_response_hash:
            return
        self.last_response_hash = sha3_256(bytes(json.dumps(response), 'utf-8')).digest()

        self.occupied_amount = response['occupied']
        self.labelOccupiedAmount.setText(amount_format(self.occupied_amount))
        self.clientStoragesExplorer.setRowCount(sum([(len(response[type])) for type in ['dirs', 'files']]))
        row = 0
        for type in ['dirs', 'files']:
            for obj in sorted(response[type], key=lambda k: k['name']):  # Отображаем отсортированные директории и файлы
                self.clientStoragesExplorer.setItem(row, 0, QTableWidgetItem(obj['id_object']))
                self.clientStoragesExplorer.setItem(row, 1, QTableWidgetItem(obj['name']))
                self.clientStoragesExplorer.setItem(row, 3, QTableWidgetItem({'dirs': 'Directory',
                                                                              'files': 'File'}[type]))
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
        self.clientStoragesExplorer.hide()
        self.clientStoragesExplorer.show()

    def show_current_file(self, id_obj):
        # Открываем файл
        data = {'address': self.get_current_client_wallet().address}
        if id_obj not in {None, ''}:
            # Передаем id объекта, если создаем новую директорию или открываем файл
            data['id_object'] = id_obj

        response = requests.get(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_object',
                                params=data)

        # Сохраняем во временные файлы и открываем
        file_name = os.path.join(os.environ['TEMP'],
                                 self.clientStoragesExplorer.item(self.clientStoragesExplorer.currentRow(), 1).text())
        with open(file_name, 'wb') as f:
            [f.write(chunk) for chunk in response.iter_content(SIZE_REPLICA)]

        os.startfile(file_name)


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
        labels = ['number block', 'recipient pool', 'amount pool', 'recipient fog node', 'amount fog node', 'transactions']
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


class FogNodesWidget(QVBoxLayout):
    createPool = pyqtSignal(str)
    changeBalance = pyqtSignal(str, int)
    createClientStorage = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.clipboard = QGuiApplication.clipboard()
        self.initUI()

    def initUI(self):
        self.mfn = ManagerFogNodes()
        self.mfn.load_fog_nodes('data/fog_nodes/key')
        self.mfn.on_change_balance = self.on_change_balance
        self.mfn.on_change_state = self.on_change_state

        labels = ['Name', 'State', 'Amount', 'Full amount']
        self.fogNodesTableWidget = QTableWidget()
        self.fogNodesTableWidget.setColumnCount(len(labels))
        self.fogNodesTableWidget.setHorizontalHeaderLabels(labels)
        self.fogNodesTableWidget.verticalHeader().hide()
        self.fogNodesTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fogNodesTableWidget.setShowGrid(False)
        self.fogNodesTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fogNodesTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.fogNodesTableWidget.setColumnHidden(3, True)
        self.fogNodesTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fogNodesTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)

        clients_address = [Wallet(key).address for key in LoadJsonFile('data/clients_manager/key').as_list()]
        for key in LoadJsonFile('data/fog_nodes/key').as_list():
            wallet = Wallet(key)
            address = wallet.address
            row = self.fogNodesTableWidget.rowCount()
            self.fogNodesTableWidget.setRowCount(row + 1)
            self.fogNodesTableWidget.setItem(row, 0, QTableWidgetItem(address))
            if address in clients_address:
                self.item(row, 0).setForeground(QColor(CLIENT_STORAGE_FOREGROUND_COLOR))

        self.fogNodesTableWidget.setSortingEnabled(True)
        self.fogNodesTableWidget.sortByColumn(0, Qt.AscendingOrder)
        self.fogNodesTableWidget.setCurrentCell(0, 0)

        self.fogNodesTableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fogNodesTableWidget.customContextMenuRequested.connect(self.fog_node_context_menu_open)
        self.fogNodesTableWidget.cellClicked.connect(self.current_item_change)

        layout = QHBoxLayout()
        self.createNodeButton = QPushButton("Create Fog_Node")
        self.createNodeButton.clicked.connect(self.create_node)
        self.create_and_open_PoolButton = QPushButton("Create Pool")
        self.create_and_open_PoolButton.clicked.connect(self.create_and_open_pool)
        self.sendByteExButton = QPushButton("Send Bytes")
        self.sendByteExButton.clicked.connect(self.send_byteEx)
        self.create_and_open_client_storageButton = QPushButton("Create Client Storage")
        self.create_and_open_client_storageButton.clicked.connect(self.create_client_storage)
        self.create_and_open_client_storageButton.setVisible(self.fogNodesTableWidget.rowCount() > 0)

        self.address_pool = LoadJsonFile('data/pool/key').as_string()
        self.create_and_open_PoolButton.setVisible(not self.address_pool and self.fogNodesTableWidget.rowCount() > 0)

        layout.addWidget(self.createNodeButton)
        layout.addWidget(self.create_and_open_PoolButton)
        layout.addWidget(self.create_and_open_client_storageButton)
        layout.addWidget(self.sendByteExButton)

        layout.addStretch(1)
        self.addLayout(layout)
        self.addWidget(self.fogNodesTableWidget)

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
                SaveJsonFile('data/pool/key', item)
                self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).setBackground(QtGui.QColor(POOL_BACKGROUND_COLOR))
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
            if self.fogNodesTableWidget.item(i, 0).text() == data['id_fog_node']:
                self.changeBalance.emit(data['id_fog_node'], data['amount'])
                # if self._current_address_client_storage == data['id_fog_node']:
                #    self.labelAmountClient.setText(self.amount_format(data["amount"]))
                #    self.current_client_storage_full_amount = data["amount"]
                self.fogNodesTableWidget.setItem(i, 2, QTableWidgetItem(amount_format(data['amount'])))
                self.fogNodesTableWidget.setItem(i, 3, QTableWidgetItem(str(data['amount'])))
                self.fogNodesTableWidget.item(i, 2).setTextAlignment(Qt.AlignRight)
                self.fogNodesTableWidget.hide()
                self.fogNodesTableWidget.show()
                break

    def on_change_state(self, data):
        no_exist_node = True
        for i in range(self.fogNodesTableWidget.rowCount()):
            if self.fogNodesTableWidget.item(i, 0).text() == data['id_fog_node']:
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

            if not LoadJsonFile('data/pool/key').as_string():
                context_menu.addAction(self.createPoolAction)

            context_menu.exec_(self.fogNodesTableWidget.viewport().mapToGlobal(position))

    def create_client_storage(self):
        self.createClientStorage.emit(self.current_fog_node())
        self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).setForeground(QColor(CLIENT_STORAGE_FOREGROUND_COLOR))


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
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.search = QLineEdit()
        self.addWidget(self.search)
        self.addStretch(1)