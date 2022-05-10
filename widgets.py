import json
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QTableWidget, QLabel, QTableWidgetItem
from PyQt5.QtCore import Qt
from utils import LoadJsonFile
from threading import Thread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QFrame
from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
from time import sleep


class ClientStoragesExplorer(QTableWidget):
    # Проводник client storage's, отображение файловой системы
    update_dir = pyqtSignal(dict)
    message = pyqtSignal(str)

    def __init__(self, name=''):
        super().__init__()
        self.update_data_thread = None
        self.clipboard = QGuiApplication.clipboard()  # Буфер обмена

        self._current_id_object = ''  # Текущий объект
        self._name = name  # Текущее имя storage
        self._last_response_hash = ''  # Хеш предыдущего запроса объекта

        labels = ['Id', 'Name', 'Date', 'Type', 'Size']  # Заголовки таблицы
        self.setColumnCount(len(labels))  # Устанавливаем количество колонок по количеству заголовков
        self.setHorizontalHeaderLabels(labels)  # Устанавливаем заголовки
        self.verticalHeader().hide()  # Скрываем нумерацию рядов
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет редактирования
        self.setShowGrid(False)  # Скрываем сетку в таблице
        self.setFrameStyle(QFrame.NoFrame)  # Скрываем рамку
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  #
        self.setSelectionMode(QAbstractItemView.SingleSelection)  #

        self.setColumnHidden(0, True)  # Id объекта, скрываем колонку
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Имя объекта, растягиваем ячейку
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Дата создания
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Тип объекта: директория, фалй
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Размер обекта в byteEx

        self.setStyleSheet("* {\n"
                           "    background: transparent;\n"
                           "    color: rgb(210, 210, 210);\n"
                           "}\n"
                           "QTableWidget {    \n"
                           "    background-color: rgb(39, 44, 54);\n"
                           "    padding: 10px;\n"
                           "    border-radius: 5px;\n"
                           "    gridline-color: rgb(44, 49, 60);\n"
                           "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                           "}\n"
                           "QTableWidget::item{\n"
                           "    border-color: rgb(44, 49, 60);\n"
                           "    padding-left: 5px;\n"
                           "    padding-right: 5px;\n"
                           "    gridline-color: rgb(44, 49, 60);\n"
                           "}\n"
                           "QTableWidget::item:selected{\n"
                           "    background-color: rgb(85, 170, 255);\n"
                           "}\n"
                           "QScrollBar:horizontal {\n"
                           "    border: none;\n"
                           "    background: rgb(52, 59, 72);\n"
                           "    height: 14px;\n"
                           "    margin: 0px 21px 0 21px;\n"
                           "    border-radius: 0px;\n"
                           "}\n"
                           " QScrollBar:vertical {\n"
                           "    border: none;\n"
                           "    background: rgb(52, 59, 72);\n"
                           "    width: 14px;\n"
                           "    margin: 21px 0 21px 0;\n"
                           "    border-radius: 0px;\n"
                           " }\n"
                           "QHeaderView::section{\n"
                           "    Background-color: rgb(39, 44, 54);\n"
                           "    max-width: 30px;\n"
                           "    border: 1px solid rgb(44, 49, 60);\n"
                           "    border-style: none;\n"
                           "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                           "    border-right: 1px solid rgb(44, 49, 60);\n"
                           "}\n"
                           "QTableWidget::horizontalHeader {    \n"
                           "    background-color: rgb(81, 255, 0);\n"
                           "}\n"
                           "QHeaderView::section:horizontal\n"
                           "{\n"
                           "    border: 1px solid rgb(32, 34, 42);\n"
                           "    background-color: rgb(27, 29, 35);\n"
                           "    padding: 3px;\n"
                           "    border-top-left-radius: 7px;\n"
                           "    border-top-right-radius: 7px;\n"
                           "}\n"
                           "/* SCROLL BARS */\n"
                           "QScrollBar:horizontal {\n"
                           "    border: none;\n"
                           "    background: rgb(52, 59, 72);\n"
                           "    height: 14px;\n"
                           "    margin: 0px 21px 0 21px;\n"
                           "    border-radius: 0px;\n"
                           "}\n"
                           "QScrollBar::handle:horizontal {\n"
                           "    background: rgb(85, 170, 255);\n"
                           "    min-width: 25px;\n"
                           "    border-radius: 7px\n"
                           "}\n"
                           "QScrollBar::add-line:horizontal {\n"
                           "    border: none;\n"
                           "    background: rgb(55, 63, 77);\n"
                           "    width: 20px;\n"
                           "    border-top-right-radius: 7px;\n"
                           "    border-bottom-right-radius: 7px;\n"
                           "    subcontrol-position: right;\n"
                           "    subcontrol-origin: margin;\n"
                           "}\n"
                           "QScrollBar::sub-line:horizontal {\n"
                           "    border: none;\n"
                           "    background: rgb(55, 63, 77);\n"
                           "    width: 20px;\n"
                           "    border-top-left-radius: 7px;\n"
                           "    border-bottom-left-radius: 7px;\n"
                           "    subcontrol-position: left;\n"
                           "    subcontrol-origin: margin;\n"
                           "}\n"
                           "QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
                           "{\n"
                           "     background: none;\n"
                           "}\n"
                           "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
                           "{\n"
                           "     background: none;\n"
                           "}\n"
                           " QScrollBar:vertical {\n"
                           "    border: none;\n"
                           "    background: rgb(52, 59, 72);\n"
                           "    width: 14px;\n"
                           "    margin: 21px 0 21px 0;\n"
                           "    border-radius: 0px;\n"
                           " }\n"
                           " QScrollBar::handle:vertical {    \n"
                           "    background: rgb(85, 170, 255);\n"
                           "    min-height: 25px;\n"
                           "    border-radius: 7px\n"
                           " }\n"
                           " QScrollBar::add-line:vertical {\n"
                           "     border: none;\n"
                           "    background: rgb(55, 63, 77);\n"
                           "     height: 20px;\n"
                           "    border-bottom-left-radius: 7px;\n"
                           "    border-bottom-right-radius: 7px;\n"
                           "     subcontrol-position: bottom;\n"
                           "     subcontrol-origin: margin;\n"
                           " }\n"
                           " QScrollBar::sub-line:vertical {\n"
                           "    border: none;\n"
                           "    background: rgb(55, 63, 77);\n"
                           "     height: 20px;\n"
                           "    border-top-left-radius: 7px;\n"
                           "    border-top-right-radius: 7px;\n"
                           "     subcontrol-position: top;\n"
                           "     subcontrol-origin: margin;\n"
                           " }\n"
                           " QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
                           "     background: none;\n"
                           " }\n"
                           "\n"
                           " QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
                           "     background: none;\n"
                           " }")
        self.itemDoubleClicked.connect(self.open_object)  # По двойному нажатию открываем объект

    def get_path(self):
        # Отправляем путь к текущей директории
        return self._name + '/' + self._current_id_object

    @property
    def current_id_dir(self):
        # Отправляем текущую директорию
        return self._current_id_object

    @current_id_dir.setter
    def current_id_dir(self, current_id_object):
        # Изменяем текущую директорию
        self._current_id_object = current_id_object

    def change_name(self, name):
        # Смена текщего имени storage
        self._name = name

    def change_path(self, path):
        # Смена пути и отображение обекта по этому пути
        if '/' in path:
            self._name, self._current_id_object = path.split('/')[:2]
        else:
            self._name = path
            self._current_id_object = ''

        if self._name == '':  # Если путь пустой, то отображаем пустой widget
            self.update_dir.emit({})
        else:
            self.show_current_object()  # Иначе обновляем  изображение окна

    def open_object(self, item):
        # Открытие объекта/переход в новую папку
        self._current_id_object = self.item(self.currentRow(), 0).text()
        # Обновляем изображение окна
        self.show_current_object()

    def show_current_object(self):
        from fog_node import SIZE_REPLICA
        from _pysha3 import sha3_256
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME

        try:
            response = requests.get(
                f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_object/{self._name}',
                params={'id_object': self._current_id_object})  # Получаем объект
        except:
            self._last_response_hash = ''
            self.message.emit('no connection')
            return

        try:
            response = response.json()  # объект типа директория приходит в формате json
            type_object = 'dir'
        except:
            type_object = 'file'  # Иначе это объект типа файл

        if 'error' in response:
            self._last_response_hash = ''
            self.message.emit(response['error'])
            self.update_data_thread = None
            return

        if not self.update_data_thread:
            self.update_data_thread = Thread(target=self.update_data)  # Создание потока для обновления данный
            self.update_data_thread.start()

        if type_object == 'dir':
            if sha3_256(bytes(json.dumps(response), 'utf-8')).hexdigest() == self._last_response_hash:
                return  # Если хеш предыдущего запроса совпадает с текщим, то не меняем изображение экрана
            self._last_response_hash = sha3_256(bytes(json.dumps(response), 'utf-8')).hexdigest()  # Перезаписываем хеш
            self.update_dir.emit(response['json'])  # Отправляем данные на отображение
        elif type_object == 'file':
            # Получаем имя файл для сохранения
            try:
                info_object = requests.get(
                    f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_info_object/{self._name}',
                    params={'id_object': self._current_id_object}).json()
            except:
                self._last_response_hash = ''
                self.message.emit('no connection')
                return
            # Сохраняем во временные файлы и открываем
            file_name = os.path.join(os.environ['TEMP'], info_object['name'])
            with open(file_name, 'wb') as f:
                [f.write(chunk) for chunk in response.iter_content(SIZE_REPLICA)]
            os.startfile(file_name)  # Отрываем файл
            if self.rowCount() and self._current_id_object != self.item(self.currentRow(), 0).text():  # Если введенный хапрос это файл
                self._last_response_hash = ''
                self.message.emit('ok')

    def update_data(self):
        while True:
            sleep(15)  # Каждые 15 секунд запрашиваем информацию об объекте
            try:
                if self._name != '':
                    info_object = requests.get(
                        f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_info_object/{self._name}',
                        params={'id_object': self._current_id_object}).json()
                    # И если нет ошибки и текуший объект - директория, то обновляем страницу
                    if 'error' not in info_object and info_object['type'] == 'dir':
                        self.show_current_object()
            except:
                self.message.emit('no connection')

    def copy_path(self):
        # Копирование а буфер обмена пути к файлу
        self.clipboard.setText(self._name + '/' + self.item(self.currentRow(), 0).text())


class ClientStorageWidget(QVBoxLayout):
    from PyQt5.QtCore import pyqtSignal
    changeNs = pyqtSignal(str, str)  # Сигнал на смену текущего имени
    openSettings = pyqtSignal()  # Сигнал на открытие настроек

    def __init__(self, parent, name: str):
        super().__init__()
        from wallet import Wallet
        from variables import DNS_NAME, PORT_DISPATCHER_CLIENTS_MANAGER
        from utils import LoadJsonFile

        self._name = name  # Текущее имя клиента
        try:  # Адрес клиента
            self._address = requests.get(
                f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/address_normal/{name}').json()
        except:
            print(f'Клиента с именем {name} не существует в сети')
            return
        self._wallet = None  # Кошелек клиента
        for key in LoadJsonFile('data/clients_manager/key').as_list():
            if Wallet(key).address == self._address:  # Получаем кошелек
                self._wallet = Wallet(key)
                break
        self._full_amount = 0  # Полный баланс клиента
        self._used_amount = 0  # Занятый баланс
        self.ui = parent.ui
        self.initUI()

    def initUI(self):
        from PyQt5.QtCore import Qt
        from utils import amount_format
        from PyQt5.QtWidgets import QLabel
        from PyQt5.QtGui import QFont

        # --------- Widget all balance ---------
        layout_balance = QHBoxLayout()
        layout_balance.addStretch(1)
        layout_v = QVBoxLayout()

        layoutAllBalance = QHBoxLayout()

        self.labelAllBalanceClient = QLabel('Full balance: ')
        font = QFont()
        font.setPointSize(9)
        self.labelAllBalanceClient.setFont(font)
        self.labelAmountClient = QLabel()
        self.labelAmountClient.setFont(font)
        layoutAllBalance.addWidget(self.labelAllBalanceClient)
        layoutAllBalance.addWidget(self.labelAmountClient)
        layout_v.addLayout(layoutAllBalance)
        # --------- Widget used balance ---------
        layoutUsedBalance = QHBoxLayout()

        self.labelUsedBalance = QLabel('Used balance: ')
        self.labelUsedBalance.setFont(font)
        self.labelUsedAmount = QLabel(amount_format(0))
        self.labelUsedAmount.setFont(font)
        layoutUsedBalance.addWidget(self.labelUsedBalance)
        layoutUsedBalance.addWidget(self.labelUsedAmount)

        layout_v.addLayout(layoutUsedBalance)
        layout_balance.addLayout(layout_v)

        # --------- Widget Message ---------
        layout = QHBoxLayout()
        self.label_message = QLabel()
        self.label_message.hide()
        layout.addWidget(self.label_message)

        # --------- Widget Explorer ---------

        self.clientStoragesExplorer = ClientStoragesExplorer(self._name)
        self.clientStoragesExplorer.update_dir.connect(self.update_dir)
        self.clientStoragesExplorer.message.connect(self.message_explorer)
        self.clientStoragesExplorer.change_path(self._name)
        # Контекстное меню
        self.clientStoragesExplorer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.clientStoragesExplorer.customContextMenuRequested.connect(self.context_menu_open)
        layout.addWidget(self.clientStoragesExplorer)
        self.clientStoragesExplorer.setCurrentCell(0, 0)

        self.addLayout(layout)
        self.addLayout(layout_balance)
        # --------- Widgets button ---------
        self.ui.createFolderButton.clicked.connect(self.create_folder)
        self.ui.sendFileButton.clicked.connect(self.send_file)
        self.ui.addNSButton.clicked.connect(self.registration_domain_name)

    @staticmethod
    def chunking(file_name):
        from fog_node import SIZE_REPLICA
        # Отправляем чанки файла
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

    def message_explorer(self, text):
        if text == 'ok':
            # Файл, скрываем message
            self.label_message.hide()
            self.clientStoragesExplorer.show()
        else:
            # Ошибка, отображаем сообщение
            self.clientStoragesExplorer.hide()
            self.label_message.setText(text)
            self.label_message.show()

    def context_menu_open(self, position):
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
        from PyQt5.QtWidgets import QAction, QMenu

        context_menu = QMenu(self.clientStoragesExplorer)

        if self.clientStoragesExplorer.itemAt(position):
            # Если нажали на ячеку, то добавляем возможность скапировать путь к объекту
            copyAction = QAction('Copy Path')
            copyAction.triggered.connect(self.clientStoragesExplorer.copy_path)
            context_menu.addAction(copyAction)
        try:
            # Запрашиваем все ns клиента
            response = requests.get(
                f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/get_all_ns/{self._address}').json()
            if response:  # Если есть хотя бы 1 ns
                useNs_menu = QMenu('Use ns')
                context_menu.addMenu(useNs_menu)
                self.ns_actions = []
                if self._name != self._address:  # Если текущее имя не адрес, то добавить адрес к ns
                    self.ns_actions = [QAction(self._address)]
                    self.ns_actions[0].triggered.connect(self.use_ns)
                    useNs_menu.addAction(self.ns_actions[0])
                    useNs_menu.addSeparator()

                for ns in response:
                    if self._name != ns:  # Если имя не равно текущему, то добавляем
                        self.ns_actions.append(QAction(ns))
                        self.ns_actions[-1].triggered.connect(self.use_ns)
                        useNs_menu.addAction(self.ns_actions[-1])
        except:
            pass

        context_menu.exec_(self.clientStoragesExplorer.viewport().mapToGlobal(position))
        self.ns_actions = None

    def use_ns(self):
        self._name = self.sender().text()
        self.changeNs.emit(self._name, self._address)  # Изменяем старое имя на новое

    def registration_domain_name(self):
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME

        addNSDialog = AddNSDialog()
        if addNSDialog.exec_() == QDialog.Accepted:
            try:
                data = {'address': self._address,
                        'name': addNSDialog.ui.nameLineEdit.text()}  # Отправляем запрос на регистрацию нового ns
                requests.post(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/registration_domain_name',
                              json=data)
            except:
                pass

    def change_balance(self, amount):
        from utils import amount_format

        self._full_amount = amount  # Перезаписываем полный баланс
        self.labelAmountClient.setText(amount_format(amount))

    def update_dir(self, data):
        from datetime import datetime
        from PyQt5.QtGui import QColor
        from utils import amount_format
        from variables import CLIENT_STORAGE_FOREGROUND_COLOR
        from PyQt5.QtWidgets import QTableWidgetItem

        if not data:  # Если даты нет, то отображаем пустой проводник
            self.clientStoragesExplorer.setRowCount(0)
            return
        self.clientStoragesExplorer.show()
        self.label_message.hide()

        self._used_amount = data['occupied']  # Обновляем использованный баланс
        self.labelUsedAmount.setText(amount_format(self._used_amount))

        self.clientStoragesExplorer.setRowCount(
            sum([(len(data[type])) for type in ['dirs', 'files']]))  # Получаем количество рядов
        row = 0
        for type in ['dirs', 'files']:
            for obj in sorted(data[type], key=lambda k: k['name']):  # Отображаем отсортированные директории и файлы
                # Скрытая ячека с id объекта
                self.clientStoragesExplorer.setItem(row, 0, QTableWidgetItem(obj['id_object']))
                # Имя объекта
                self.clientStoragesExplorer.setItem(row, 1, QTableWidgetItem(obj['name']))
                # Тип объекта
                self.clientStoragesExplorer.setItem(row, 3,
                                                    QTableWidgetItem({'dirs': 'Directory', 'files': 'File'}[type]))
                # Если info есть в ключах, значит объект зарегистрирован в блокчейне, отображаем информацию
                if 'info' in obj.keys() and obj['info']:
                    # Перекрашиваем текст имени обекта в зеленый
                    self.clientStoragesExplorer.item(row, 1).setForeground(QColor(CLIENT_STORAGE_FOREGROUND_COLOR))
                    # Дата созания/регистрации в блокчене
                    self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(
                        datetime.fromtimestamp(obj['info']['date']).strftime('%Y-%m-%d %H:%M:%S')))
                    # Размер объекта
                    self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(amount_format(obj['info']['size'])))
                elif obj['name'] == '..':  # Переход на директорию выше
                    self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(''))  # Дата и размер отсутствуют
                    self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(''))
                else:
                    # Иначе объект не зарегистрирован в блокчене
                    self.clientStoragesExplorer.item(row, 1).setForeground(QColor('red'))  # Цвет имени - красный
                    # Времено отображаем дату создания
                    self.clientStoragesExplorer.setItem(row, 2, QTableWidgetItem(
                        datetime.fromtimestamp(datetime.utcnow().timestamp()).strftime('%Y-%m-%d %H:%M:%S')))
                    self.clientStoragesExplorer.setItem(row, 4, QTableWidgetItem(amount_format(0)))  # Размер = 0
                row += 1

    def create_folder(self):
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
        from PyQt5.QtWidgets import QMessageBox

        createFolderDialog = CreateFolderDialog()
        if createFolderDialog.exec_() == QDialog.Accepted:
            # Проверяем чтобы хватило места для создания директории
            if 400 + self._used_amount > self._full_amount:
                QMessageBox.critical(self.clientStoragesExplorer, "Error", "Не хватает места", QMessageBox.Ok)
                return
            name = createFolderDialog.ui.nameFolderLineEdit.text()
            data = {'name': name}
            id_current_dir = self.clientStoragesExplorer.current_id_dir
            if id_current_dir:
                data['id_current_dir'] = id_current_dir
            data = self.signed_data_request(data)
            response = requests.get(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/make_dir',
                                    json=data).json()
            if 'error' in response:
                QMessageBox.critical(self.clientStoragesExplorer, "Error", response['error'], QMessageBox.Ok)
                return
            self.clientStoragesExplorer.current_id_dir = id_current_dir
            self.clientStoragesExplorer.show_current_object()

    def send_file(self):
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
        from PyQt5.QtWidgets import QMessageBox, QFileDialog

        # Загрузка файла
        path = QFileDialog.getOpenFileName(self.clientStoragesExplorer, "Select a file...",
                                           None, filter="All files (*)")[0]
        if path.strip():
            if os.path.getsize(path) + self._used_amount > self._full_amount:
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
                return
            self.clientStoragesExplorer.current_id_dir = id_current_dir
            self.clientStoragesExplorer.show_current_object()

    def open_menu_settings(self):
        self.openSettings.emit()


class PoolWidget(QVBoxLayout):
    def __init__(self, parent):
        super().__init__()
        self.pool = None
        self._address_pool = None
        self.pool_balance = 0
        self._is_run = False  # Флаг на запущенл ли пул
        self.ui = parent.ui
        self.port_pool = parent.port_pool
        self.port_cm = parent.port_cm
        self.port_fn = parent.port_fn
        self.initUI()

    def initUI(self):
        from utils import amount_format, LoadJsonFile
        from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QFrame, QListWidget
        from PyQt5.QtGui import QFont
        from PyQt5.QtCore import Qt

        font = QFont()
        font.setPointSize(9)
        layout = QHBoxLayout()
        self.label_1 = QLabel('All active Fog Nodes: ')
        self.label_1.setFont(font)
        self.AllActiveFogNodesLabel = QLabel('0')
        self.AllActiveFogNodesLabel.setFont(font)
        layout.addWidget(self.label_1)
        layout.addWidget(self.AllActiveFogNodesLabel)
        layout.addStretch(1)
        self.label_2 = QLabel('All active Pools: ')
        self.label_2.setFont(font)
        self.AllActivePoolsLabel = QLabel('0')
        self.AllActivePoolsLabel.setFont(font)
        layout.addWidget(self.label_2)
        layout.addWidget(self.AllActivePoolsLabel)
        self.addLayout(layout)
        # --------- Widget information blockchain ---------
        labels = ['Number', 'Pool', 'Fog Node', 'Date', 'Data']  # Заголовки таблицы
        self.infoBlockchain = QTableWidget()
        self.infoBlockchain.setColumnCount(len(labels))  # Устанавливаем количество колонок по количеству заголовков
        self.infoBlockchain.setHorizontalHeaderLabels(labels)  # Устанавливаем заголовки
        self.infoBlockchain.verticalHeader().hide()  # Скрываем нумерацию рядов
        self.infoBlockchain.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет редактирования
        self.infoBlockchain.setShowGrid(False)  # Скрываем сетку в таблице
        self.infoBlockchain.setFrameStyle(QFrame.NoFrame)  # Скрываем рамку

        self.infoBlockchain.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.infoBlockchain.setColumnHidden(4, True)

        self.infoBlockchain.setStyleSheet("* {\n"
                                          "    background: transparent;\n"
                                          "    color: rgb(210, 210, 210);\n"
                                          "}\n"
                                          "QTableWidget {    \n"
                                          "    background-color: rgb(39, 44, 54);\n"
                                          "    padding: 10px;\n"
                                          "    border-radius: 5px;\n"
                                          "    gridline-color: rgb(44, 49, 60);\n"
                                          "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                                          "}\n"
                                          "QTableWidget::item{\n"
                                          "    border-color: rgb(44, 49, 60);\n"
                                          "    padding-left: 5px;\n"
                                          "    padding-right: 5px;\n"
                                          "    gridline-color: rgb(44, 49, 60);\n"
                                          "}\n"
                                          "QTableWidget::item:selected{\n"
                                          "    background-color: rgb(85, 170, 255);\n"
                                          "}\n"
                                          "QScrollBar:horizontal {\n"
                                          "    border: none;\n"
                                          "    background: rgb(52, 59, 72);\n"
                                          "    height: 14px;\n"
                                          "    margin: 0px 21px 0 21px;\n"
                                          "    border-radius: 0px;\n"
                                          "}\n"
                                          " QScrollBar:vertical {\n"
                                          "    border: none;\n"
                                          "    background: rgb(52, 59, 72);\n"
                                          "    width: 14px;\n"
                                          "    margin: 21px 0 21px 0;\n"
                                          "    border-radius: 0px;\n"
                                          " }\n"
                                          "QHeaderView::section{\n"
                                          "    Background-color: rgb(39, 44, 54);\n"
                                          "    max-width: 30px;\n"
                                          "    border: 1px solid rgb(44, 49, 60);\n"
                                          "    border-style: none;\n"
                                          "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                                          "    border-right: 1px solid rgb(44, 49, 60);\n"
                                          "}\n"
                                          "QTableWidget::horizontalHeader {    \n"
                                          "    background-color: rgb(81, 255, 0);\n"
                                          "}\n"
                                          "QHeaderView::section:horizontal\n"
                                          "{\n"
                                          "    border: 1px solid rgb(32, 34, 42);\n"
                                          "    background-color: rgb(27, 29, 35);\n"
                                          "    padding: 3px;\n"
                                          "    border-top-left-radius: 7px;\n"
                                          "    border-top-right-radius: 7px;\n"
                                          "}\n"
                                          "QHeaderView::section:vertical\n"
                                          "{\n"
                                          "    border: 1px solid rgb(44, 49, 60);\n"
                                          "}\n"
                                          "\n"
                                          "/* SCROLL BARS */\n"
                                          "QScrollBar:horizontal {\n"
                                          "    border: none;\n"
                                          "    background: rgb(52, 59, 72);\n"
                                          "    height: 14px;\n"
                                          "    margin: 0px 21px 0 21px;\n"
                                          "    border-radius: 0px;\n"
                                          "}\n"
                                          "QScrollBar::handle:horizontal {\n"
                                          "    background: rgb(85, 170, 255);\n"
                                          "    min-width: 25px;\n"
                                          "    border-radius: 7px\n"
                                          "}\n"
                                          "QScrollBar::add-line:horizontal {\n"
                                          "    border: none;\n"
                                          "    background: rgb(55, 63, 77);\n"
                                          "    width: 20px;\n"
                                          "    border-top-right-radius: 7px;\n"
                                          "    border-bottom-right-radius: 7px;\n"
                                          "    subcontrol-position: right;\n"
                                          "    subcontrol-origin: margin;\n"
                                          "}\n"
                                          "QScrollBar::sub-line:horizontal {\n"
                                          "    border: none;\n"
                                          "    background: rgb(55, 63, 77);\n"
                                          "    width: 20px;\n"
                                          "    border-top-left-radius: 7px;\n"
                                          "    border-bottom-left-radius: 7px;\n"
                                          "    subcontrol-position: left;\n"
                                          "    subcontrol-origin: margin;\n"
                                          "}\n"
                                          "QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
                                          "{\n"
                                          "     background: none;\n"
                                          "}\n"
                                          "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
                                          "{\n"
                                          "     background: none;\n"
                                          "}\n"
                                          " QScrollBar:vertical {\n"
                                          "    border: none;\n"
                                          "    background: rgb(52, 59, 72);\n"
                                          "    width: 14px;\n"
                                          "    margin: 21px 0 21px 0;\n"
                                          "    border-radius: 0px;\n"
                                          " }\n"
                                          " QScrollBar::handle:vertical {    \n"
                                          "    background: rgb(85, 170, 255);\n"
                                          "    min-height: 25px;\n"
                                          "    border-radius: 7px\n"
                                          " }\n"
                                          " QScrollBar::add-line:vertical {\n"
                                          "     border: none;\n"
                                          "    background: rgb(55, 63, 77);\n"
                                          "     height: 20px;\n"
                                          "    border-bottom-left-radius: 7px;\n"
                                          "    border-bottom-right-radius: 7px;\n"
                                          "     subcontrol-position: bottom;\n"
                                          "     subcontrol-origin: margin;\n"
                                          " }\n"
                                          " QScrollBar::sub-line:vertical {\n"
                                          "    border: none;\n"
                                          "    background: rgb(55, 63, 77);\n"
                                          "     height: 20px;\n"
                                          "    border-top-left-radius: 7px;\n"
                                          "    border-top-right-radius: 7px;\n"
                                          "     subcontrol-position: top;\n"
                                          "     subcontrol-origin: margin;\n"
                                          " }\n"
                                          " QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
                                          "     background: none;\n"
                                          " }\n"
                                          "\n"
                                          " QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
                                          "     background: none;\n"
                                          " }")
        self.infoBlockchain.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.infoBlockchain.setSelectionMode(QAbstractItemView.SingleSelection)
        self.infoBlockchain.setCurrentCell(0, 0)
        self.infoBlockchain.doubleClicked.connect(self.show_info_block)  # Обработка на нажатие на ячейку
        self.addWidget(self.infoBlockchain)

        # --------- Widget all balance ---------
        layout = QHBoxLayout()
        self.label = QLabel('Address Pool: ')
        self.label.setFont(font)
        self.addressPoolLabel = QLabel(amount_format(0))
        self.addressPoolLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.addressPoolLabel.setFont(font)
        layout.addWidget(self.label)
        layout.addWidget(self.addressPoolLabel)
        layout.setSpacing(15)
        self.labelFullBalancePool = QLabel('Full balance: ')
        self.labelFullBalancePool.setFont(font)
        self.labelAmountPool = QLabel(amount_format(0))
        self.labelAmountPool.setFont(font)
        layout.addStretch(1)
        layout.addWidget(self.labelFullBalancePool)
        layout.addWidget(self.labelAmountPool)
        self.addLayout(layout)

        private_key = LoadJsonFile('data/pool/key').as_string()
        if private_key:  # В файле всегда 1 ключ, если он есть, значит пул уже был создан, поэтому запускаем пул
            self.start_pool(private_key)

    def stop(self):
        from time import sleep
        print(self.pool)
        if self.pool:
            try:
                self.client_app.request(method='stop')
            except:
                pass
            self.client_app.stop()
            while self.client_app.is_alive():
                sleep(0.1)

    def show_info_block(self):
        infoBlock = InfoBlockDialog(json.loads(self.infoBlockchain.item(self.infoBlockchain.currentRow(), 4).text()))
        infoBlock.exec_()

    def add_new_block(self, data):
        row = self.infoBlockchain.rowCount()
        self.infoBlockchain.insertRow(0)
        self.infoBlockchain.setItem(0, 0, QTableWidgetItem(str(data['number'])))
        self.infoBlockchain.setItem(0, 1, QTableWidgetItem(data['recipient_pool']))
        self.infoBlockchain.setItem(0, 2, QTableWidgetItem(data['recipient_fog_node']))
        self.infoBlockchain.setItem(0, 3, QTableWidgetItem(
            datetime.fromtimestamp(data['date']).strftime('%Y-%m-%d %H:%M:%S')))
        self.infoBlockchain.setItem(0, 4, QTableWidgetItem(json.dumps(data)))
        if row > 100:
            self.infoBlockchain.removeRow(row)

    def is_run(self):
        return self._is_run

    def update_active(self, data):
        print(data)

    def start_pool(self, private_key):
        from pool import Pool
        from wallet import Wallet
        from dctp import ClientDCTP
        from variables import DNS_IP, PORT_APP

        try:
            self.pool = Pool(private_key=private_key, port_pool=self.port_pool, port_cm=self.port_cm,
                             port_fn=self.port_fn, port_app=PORT_APP)
            self.pool.start()
        except Exception as e:
            print(e)
            return
        self._address_pool = Wallet(private_key).address
        self.addressPoolLabel.setText(self._address_pool)
        self._is_run = True
        client_app = ClientDCTP(self._address_pool, DNS_IP, PORT_APP, reconnect=True)

        @client_app.method('update_app_pool')
        def update_app_pool(json, data):
            self.add_new_block(json['block'])
            self.AllActiveFogNodesLabel.setText(str(json['active_fog_nodes']))
            self.AllActivePoolsLabel.setText(str(json['active_pool']))

        client_app.start()
        self.client_app = client_app

    def change_balance_pool(self, amount):
        from utils import amount_format

        self.pool_balance = amount  # Обновляем полный баланс пула
        self.labelAmountPool.setText(amount_format(amount))


class FogNodesWidget(QHBoxLayout):
    changeBalanceClientsStorage = pyqtSignal(str, int)  # Сигнал на изменение баланса клиента
    changeBalancePool = pyqtSignal(int)  # Сигнал на изменение баланса пула

    def __init__(self, parent):
        super().__init__()
        self.ui = parent.ui
        self.clipboard = QGuiApplication.clipboard()  # Буфер обмена
        self.initUI()

    def initUI(self):
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        from fog_nodes_manager import ManagerFogNodes
        from wallet import Wallet
        from utils import LoadJsonFile
        from variables import CLIENT_STORAGE_FOREGROUND_COLOR
        from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem, QFrame

        # --------- Foge Nodes ---------
        labels = ['Name', 'State', 'Amount', 'Full amount', 'Normal Address']  # Заголовки таблицы
        self.fogNodesTableWidget = QTableWidget()
        self.fogNodesTableWidget.setColumnCount(
            len(labels))  # # Устанавливаем количество колонок по количеству заголовков
        self.fogNodesTableWidget.setHorizontalHeaderLabels(labels)  # Устанавливаем заголовки
        self.fogNodesTableWidget.verticalHeader().hide()  # Скрываем нумерацию рядов
        self.fogNodesTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет редактирования
        self.fogNodesTableWidget.setShowGrid(False)  # Скрываем сетку в таблице
        self.fogNodesTableWidget.setFrameStyle(QFrame.NoFrame)  # Скрываем рамку

        self.fogNodesTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fogNodesTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.fogNodesTableWidget.setColumnHidden(3, True)  # Скрываем 3 ячейку - баланс в байтах
        self.fogNodesTableWidget.setColumnHidden(4, True)  # Скрываем 4 ячейку - адрес
        self.fogNodesTableWidget.setStyleSheet("* {\n"
                                               "    background: transparent;\n"
                                               "    color: rgb(210, 210, 210);\n"
                                               "}\n"
                                               "QTableWidget {    \n"
                                               "    background-color: rgb(39, 44, 54);\n"
                                               "    padding: 10px;\n"
                                               "    border-radius: 5px;\n"
                                               "    gridline-color: rgb(44, 49, 60);\n"
                                               "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                                               "}\n"
                                               "QTableWidget::item{\n"
                                               "    border-color: rgb(44, 49, 60);\n"
                                               "    padding-left: 5px;\n"
                                               "    padding-right: 5px;\n"
                                               "    gridline-color: rgb(44, 49, 60);\n"
                                               "}\n"
                                               "QTableWidget::item:selected{\n"
                                               "    background-color: rgb(85, 170, 255);\n"
                                               "}\n"
                                               "QScrollBar:horizontal {\n"
                                               "    border: none;\n"
                                               "    background: rgb(52, 59, 72);\n"
                                               "    height: 14px;\n"
                                               "    margin: 0px 21px 0 21px;\n"
                                               "    border-radius: 0px;\n"
                                               "}\n"
                                               " QScrollBar:vertical {\n"
                                               "    border: none;\n"
                                               "    background: rgb(52, 59, 72);\n"
                                               "    width: 14px;\n"
                                               "    margin: 21px 0 21px 0;\n"
                                               "    border-radius: 0px;\n"
                                               " }\n"
                                               "QHeaderView::section{\n"
                                               "    Background-color: rgb(39, 44, 54);\n"
                                               "    max-width: 30px;\n"
                                               "    border: 1px solid rgb(44, 49, 60);\n"
                                               "    border-style: none;\n"
                                               "    border-bottom: 1px solid rgb(44, 49, 60);\n"
                                               "    border-right: 1px solid rgb(44, 49, 60);\n"
                                               "}\n"
                                               "QTableWidget::horizontalHeader {    \n"
                                               "    background-color: rgb(81, 255, 0);\n"
                                               "}\n"
                                               "QHeaderView::section:horizontal\n"
                                               "{\n"
                                               "    border: 1px solid rgb(32, 34, 42);\n"
                                               "    background-color: rgb(27, 29, 35);\n"
                                               "    padding: 3px;\n"
                                               "    border-top-left-radius: 7px;\n"
                                               "    border-top-right-radius: 7px;\n"
                                               "}\n"
                                               "QHeaderView::section:vertical\n"
                                               "{\n"
                                               "    border: 1px solid rgb(44, 49, 60);\n"
                                               "}\n"
                                               "\n"
                                               "/* SCROLL BARS */\n"
                                               "QScrollBar:horizontal {\n"
                                               "    border: none;\n"
                                               "    background: rgb(52, 59, 72);\n"
                                               "    height: 14px;\n"
                                               "    margin: 0px 21px 0 21px;\n"
                                               "    border-radius: 0px;\n"
                                               "}\n"
                                               "QScrollBar::handle:horizontal {\n"
                                               "    background: rgb(85, 170, 255);\n"
                                               "    min-width: 25px;\n"
                                               "    border-radius: 7px\n"
                                               "}\n"
                                               "QScrollBar::add-line:horizontal {\n"
                                               "    border: none;\n"
                                               "    background: rgb(55, 63, 77);\n"
                                               "    width: 20px;\n"
                                               "    border-top-right-radius: 7px;\n"
                                               "    border-bottom-right-radius: 7px;\n"
                                               "    subcontrol-position: right;\n"
                                               "    subcontrol-origin: margin;\n"
                                               "}\n"
                                               "QScrollBar::sub-line:horizontal {\n"
                                               "    border: none;\n"
                                               "    background: rgb(55, 63, 77);\n"
                                               "    width: 20px;\n"
                                               "    border-top-left-radius: 7px;\n"
                                               "    border-bottom-left-radius: 7px;\n"
                                               "    subcontrol-position: left;\n"
                                               "    subcontrol-origin: margin;\n"
                                               "}\n"
                                               "QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
                                               "{\n"
                                               "     background: none;\n"
                                               "}\n"
                                               "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
                                               "{\n"
                                               "     background: none;\n"
                                               "}\n"
                                               " QScrollBar:vertical {\n"
                                               "    border: none;\n"
                                               "    background: rgb(52, 59, 72);\n"
                                               "    width: 14px;\n"
                                               "    margin: 21px 0 21px 0;\n"
                                               "    border-radius: 0px;\n"
                                               " }\n"
                                               " QScrollBar::handle:vertical {    \n"
                                               "    background: rgb(85, 170, 255);\n"
                                               "    min-height: 25px;\n"
                                               "    border-radius: 7px\n"
                                               " }\n"
                                               " QScrollBar::add-line:vertical {\n"
                                               "     border: none;\n"
                                               "    background: rgb(55, 63, 77);\n"
                                               "     height: 20px;\n"
                                               "    border-bottom-left-radius: 7px;\n"
                                               "    border-bottom-right-radius: 7px;\n"
                                               "     subcontrol-position: bottom;\n"
                                               "     subcontrol-origin: margin;\n"
                                               " }\n"
                                               " QScrollBar::sub-line:vertical {\n"
                                               "    border: none;\n"
                                               "    background: rgb(55, 63, 77);\n"
                                               "     height: 20px;\n"
                                               "    border-top-left-radius: 7px;\n"
                                               "    border-top-right-radius: 7px;\n"
                                               "     subcontrol-position: top;\n"
                                               "     subcontrol-origin: margin;\n"
                                               " }\n"
                                               " QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
                                               "     background: none;\n"
                                               " }\n"
                                               "\n"
                                               " QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
                                               "     background: none;\n"
                                               " }")
        self.fogNodesTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fogNodesTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)

        private_key_pool = LoadJsonFile('data/pool/key').as_string()
        if private_key_pool:  # Получаем адрес пула
            self._address_pool = Wallet(private_key_pool).address
        else:
            self._address_pool = ''

        clients_address = [Wallet(key).address for key in LoadJsonFile('data/clients_manager/key').as_list()]
        row = 0
        for key in LoadJsonFile('data/fog_nodes/key').as_list():  # Добавляем все fog nodes
            address = Wallet(key).address
            self.fogNodesTableWidget.setRowCount(row + 1)
            self.fogNodesTableWidget.setItem(row, 0, QTableWidgetItem(address))  # Устанавливаем имя node
            self.fogNodesTableWidget.setItem(row, 4, QTableWidgetItem(address))  # Устанавливаем адрес node
            if address in clients_address:  # Если node являестся client storage, то меняем стиль
                self.fogNodesTableWidget.item(row, 0).setForeground(QColor(CLIENT_STORAGE_FOREGROUND_COLOR))
            row += 1

        self.fogNodesTableWidget.setSortingEnabled(True)  # Устанавливаем сортировку
        self.fogNodesTableWidget.sortByColumn(0, Qt.AscendingOrder)
        self.fogNodesTableWidget.setCurrentCell(0, 0)

        # Создаем контекстное меню
        self.fogNodesTableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fogNodesTableWidget.customContextMenuRequested.connect(self._context_menu_open)

        self.fogNodesTableWidget.cellClicked.connect(self.current_item_change)  # Обработка на нажатие на ячейку

        self.mfn = ManagerFogNodes()
        self.mfn.load_fog_nodes()
        self.mfn.on_change_balance = self.on_change_balance
        self.mfn.on_change_state = self.on_change_state

        self.addWidget(self.fogNodesTableWidget)
        self.addSpacing(10)

    def current_item_change(self, row, column):
        from variables import CLIENT_STORAGE_FOREGROUND_COLOR

        self.ui.openPoolButton.setVisible(bool(self._address_pool))
        self.ui.createPoolButton.setVisible(not self._address_pool)
        # Изменяем подсказку и изображение кнопки
        if self.fogNodesTableWidget.item(row, 0).foreground().color().name() == CLIENT_STORAGE_FOREGROUND_COLOR:
            self.ui.openClientStorageButton.setText('    Open Client Storage')
        else:
            self.ui.openClientStorageButton.setText('    Create Client Storage')

    def create_pool(self):
        from wallet import Wallet
        from utils import LoadJsonFile

        self.ui.createPoolButton.hide()
        self.ui.openPoolButton.show()

        address = self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 4).text()
        for key in LoadJsonFile('data/fog_nodes/key').as_list():
            if Wallet(key).address == address:
                self._address_pool = address
                return key

    def current_fog_node(self):
        # Возвращаем имя текущего ряда, если есть хотя бы 1 ряд, иначе ''
        if self.fogNodesTableWidget.rowCount() > 0:
            return self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).text()
        return ""

    def _copy_fog_node_address(self):
        self.clipboard.setText(self.current_fog_node())

    def create_node(self):
        # Создаем новую node
        self.mfn.add_fog_node()
        self.ui.createPoolButton.setVisible(self._address_pool == '')
        self.ui.openPoolButton.setVisible(self._address_pool != '')
        self.ui.openClientStorageButton.setVisible(True)

    def on_change_balance(self, data):
        from PyQt5.QtCore import Qt
        from utils import amount_format
        from PyQt5.QtWidgets import QTableWidgetItem

        for i in range(self.fogNodesTableWidget.rowCount()):
            if self.fogNodesTableWidget.item(i, 4).text() == data['id_fog_node']:
                # Изменяем баланс нады, чей адрес совпадает с отправленным
                self.fogNodesTableWidget.setItem(i, 2, QTableWidgetItem(amount_format(data['amount'])))  # Новый баланс
                self.fogNodesTableWidget.setItem(i, 3, QTableWidgetItem(str(data['amount'])))  # Новый баланс в байтах
                self.fogNodesTableWidget.item(i, 2).setTextAlignment(Qt.AlignRight)
                if self.fogNodesTableWidget.item(i, 4).text() == self._address_pool:
                    # Если нода является пулом, то меняем и баланс пула
                    self.changeBalancePool.emit(data['amount'])
                self.changeBalanceClientsStorage.emit(self.fogNodesTableWidget.item(i, 0).text(), data['amount'])
                self.fogNodesTableWidget.hide()
                self.fogNodesTableWidget.show()
                return

    def on_change_state(self, data):
        # Изменение состояния fog node
        from PyQt5.QtGui import QColor
        from variables import BACKGROUND_COLOR
        from PyQt5.QtWidgets import QTableWidgetItem

        no_exist_node = True  # Флаг на существование ноды в таблийе
        for i in range(self.fogNodesTableWidget.rowCount()):
            if self.fogNodesTableWidget.item(i, 4).text() == data['id_fog_node']:
                self.fogNodesTableWidget.setItem(i, 1, QTableWidgetItem(data['state']))
                self.fogNodesTableWidget.hide()  # Для отрисовки таблицы
                self.fogNodesTableWidget.show()
                no_exist_node = False
                break

        if no_exist_node:  # Состояние пришла первый раз, создаем ряд
            row = self.fogNodesTableWidget.rowCount()
            self.fogNodesTableWidget.setRowCount(row + 1)
            # Добавляем новый ряд в таблицу без сортировки, чтобы другие ряды не сбились
            self.fogNodesTableWidget.setSortingEnabled(False)
            self.fogNodesTableWidget.setItem(row, 0, QTableWidgetItem(data['id_fog_node']))
            self.fogNodesTableWidget.item(row, 0).setBackground(QColor(BACKGROUND_COLOR))
            self.fogNodesTableWidget.setItem(row, 4, QTableWidgetItem(data['id_fog_node']))
            self.fogNodesTableWidget.setItem(row, 1, QTableWidgetItem(data['state']))
            self.fogNodesTableWidget.setItem(row, 3, QTableWidgetItem('0'))
            self.fogNodesTableWidget.setCurrentCell(row, 0)
            self.fogNodesTableWidget.setSortingEnabled(True)
        print(f'Node {data["id_fog_node"]} {data["state"]}')

    def _context_menu_open(self, position):
        from PyQt5.QtWidgets import QAction, QMenu

        if self.fogNodesTableWidget.itemAt(position):
            # Если нажали на ячеку, то добавляем возможность скапировать путь к объекту
            context_menu = QMenu(self.fogNodesTableWidget)
            copyFogNodeAction = QAction('Copy address', self)
            copyFogNodeAction.triggered.connect(self._copy_fog_node_address)
            context_menu.addAction(copyFogNodeAction)
            context_menu.exec_(self.fogNodesTableWidget.viewport().mapToGlobal(position))

    def create_client_storage(self):
        # Создание клиентского хранилища
        from PyQt5.QtGui import QColor
        from variables import CLIENT_STORAGE_FOREGROUND_COLOR
        from utils import LoadJsonFile
        from wallet import Wallet

        self.ui.openClientStorageButton.setText('    Open Client Storage')  # Изменение стилей кнопки с create -> open
        for key in LoadJsonFile('data/fog_nodes/key').as_list():
            if Wallet(key).address == self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 4).text():
                if key not in LoadJsonFile('data/clients_manager/key').as_list():
                    Wallet(key).save_private_key('data/clients_manager/key')
                    break
        self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).setForeground(
            QColor(CLIENT_STORAGE_FOREGROUND_COLOR))  # Изменение стилейв таблице fog nodes
        return self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).text()


class Send_ByteEx(QDialog):
    def __init__(self, sender: str):
        super().__init__()
        # Модальное окно для отправки byteEx
        from interface import Ui_SendByteExDialog
        from PyQt5.QtGui import QIntValidator
        from PyQt5.QtCore import Qt

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.ui = Ui_SendByteExDialog()
        self.ui.setupUi(self)
        self.ui.senderLineEdit.setText(sender)
        self.ui.amountLineEdit.setValidator(QIntValidator(0, 10000000, self))
        self.ui.okButton.clicked.connect(self.send_request)
        self.ui.cancelButton.clicked.connect(self.reject)

        def moveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

        self.ui.headerContainer.mouseMoveEvent = moveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def send_request(self):
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
        from PyQt5.QtWidgets import QMessageBox
        sender = self.ui.senderLineEdit.text().strip()
        owner = self.ui.ownerLineEdit.text().strip()
        amount = self.ui.amountLineEdit.text().strip()
        if not sender or not owner or not amount or int(amount) == 0:
            return
        amount = int(self.ui.amountLineEdit.text())
        try:  # Получаем баланс, которым может воспользываться пользователь
            response = requests.get(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/'
                                    f'api/get_free_balance/{sender}').json()
        except:
            QMessageBox.critical(self, "Error", 'Error connection', QMessageBox.Ok)
            return

        if response['status'] == 100:
            QMessageBox.critical(self, "Error", response['status_text'], QMessageBox.Ok)
            return

        if amount <= response['amount_free_balance']:  # Валидация на отправляемую сумму
            transaction = {'sender': sender, 'owner': owner,
                           'count': amount}
            try:  # Формирование и отправка транзакции
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
            QMessageBox.critical(self, "Error", f"{sender} don't have enough byteEx", QMessageBox.Ok)


class SearchClientStorage(QVBoxLayout):
    from PyQt5.QtCore import pyqtSignal
    from PyQt5.QtWidgets import QLineEdit
    changeSearchState = pyqtSignal(str)

    class Message(QVBoxLayout):
        def __init__(self, text):
            super().__init__()
            from PyQt5.QtGui import QFont

            self.text = text
            self.addStretch(1)
            layout = QHBoxLayout()
            self.addLayout(layout)
            self.label_message = QLabel(text)
            self.label_message.setFont(QFont("Verdana", 15))
            self.label_message.setStyleSheet("""color: red;""")
            layout.addStretch(1)
            layout.addWidget(self.label_message)
            layout.addStretch(1)
            self.addStretch(1)

    class QSearchLineEdit(QLineEdit):
        from PyQt5.QtCore import pyqtSignal
        enterPress = pyqtSignal()

        def __init__(self):
            super().__init__()

        def keyPressEvent(self, event):
            super().keyPressEvent(event)
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                self.enterPress.emit()

    def __init__(self, parent):
        super().__init__()
        self.ui = parent.ui
        self.initUI()
        self.message = None

    def initUI(self):
        from PyQt5.QtGui import QFont
        from PyQt5.QtWidgets import QHBoxLayout, QPushButton

        # ------------ Widgets search ------------
        layout = QHBoxLayout()
        self.search = self.QSearchLineEdit()
        self.search.setToolTip('Введите путь для отображения объекта')
        self.search.setFont(QFont("Verdana", 8))
        self.search.setStyleSheet("""QLineEdit {
                                      outline: none;
                                      background: transparent;
                                    }
                                    QLineEdit {
                                      width: 100%;
                                      height: 30px;
                                      padding-left: 15px;
                                      border: 3px solid #679ED1;
                                    }
                                    QLineEdit:focus {
                                      border-color: #4B7CA8;
                                    }""")
        self.search.enterPress.connect(self.search_path)

        layout.addWidget(self.search, stretch=5)
        self.searchButton = QPushButton()
        self.searchButton.setStyleSheet("""QPushButton {
                                            background-repeat:none;
                                            background-position: center;
                                            background-image: url(:/icons/icons/search.svg);
                                            }
                                            QPushButton:hover {
                                            background-image: url(:/icons/icons/search(1).svg);
                                            }
        """)
        self.searchButton.setMinimumSize(30, 30)
        layout.addWidget(self.searchButton)
        self.addLayout(layout)
        self.searchButton.clicked.connect(self.search_path)
        # ------------ Widgets explorer ------------
        self.clientStoragesExplorer = ClientStoragesExplorer()
        self.clientStoragesExplorer.update_dir.connect(self.update_dir)
        self.clientStoragesExplorer.message.connect(self.message_explorer)
        self.clientStoragesExplorer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.clientStoragesExplorer.customContextMenuRequested.connect(self.context_menu_open)
        self.clientStoragesExplorer.hide()
        self.addWidget(self.clientStoragesExplorer)

    def search_path(self):
        path = self.search.text()  # Путь указанный в строке поиска
        if self.message:
            self.message.label_message.hide()
            self.removeItem(self.message)
            self.message = None

        if path != self.clientStoragesExplorer.get_path():
            # Изменяем состояние приложения, если указаный путь стал новым
            self.changeSearchState.emit(path)
        self.clientStoragesExplorer.change_path(path)  # Отображаем путь

    def update_dir(self, data):
        from datetime import datetime
        from utils import amount_format
        from PyQt5.QtWidgets import QTableWidgetItem

        if not data:  # Если дата пустая, то отображаем пустой проводник
            self.clientStoragesExplorer.setRowCount(0)
            return
        self.search.setText(data['address'] + '/' + data['id_object'])  # Изменение строки поиска по текущему объекту

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

    def context_menu_open(self, position):
        from PyQt5.QtWidgets import QAction, QMenu

        if self.clientStoragesExplorer.itemAt(position):
            # Если нажали на ячеку, то добавляем возможность скапировать путь к объекту
            context_menu = QMenu(self.clientStoragesExplorer)
            copyAction = QAction('Copy Path')
            copyAction.triggered.connect(self.clientStoragesExplorer.copy_path)
            context_menu.addAction(copyAction)
            context_menu.exec_(self.clientStoragesExplorer.viewport().mapToGlobal(position))

    def message_explorer(self, text):
        if text == 'ok':
            # Файл
            self.message = self.Message('')
            self.addLayout(self.message)
            self.clientStoragesExplorer.hide()
        else:
            # Ошибка
            self.clientStoragesExplorer.hide()
            self.message = self.Message(text)
            self.addLayout(self.message)


class AllClientStorages(QDialog):
    def __init__(self):
        super().__init__()
        from interface import Ui_AllClientStoragesDialog
        from wallet import Wallet
        from PyQt5.QtCore import Qt

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ui = Ui_AllClientStoragesDialog()
        self.ui.setupUi(self)

        self.ui.okButton.clicked.connect(self.selected_client_storage)
        self.ui.cancelButton.clicked.connect(self.reject)

        for key in LoadJsonFile('data/clients_manager/key').as_list():
            self.ui.listWidget.addItem(Wallet(key).address)
        self.ui.listWidget.doubleClicked.connect(self.selected_client_storage)
        if self.ui.listWidget.count():
            self.ui.listWidget.setCurrentRow(0)

        def moveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

        self.ui.headerContainer.mouseMoveEvent = moveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def selected_client_storage(self):
        if self.ui.listWidget.count():
            self.accept()


class CreateFolderDialog(QDialog):
    def __init__(self):
        super().__init__()
        from interface import Ui_CreateFolderDialog

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ui = Ui_CreateFolderDialog()
        self.ui.setupUi(self)

        self.ui.okButton.clicked.connect(self.validation_name)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.nameFolderLineEdit.enterPress.connect(self.validation_name)
        self.ui.nameFolderLineEdit.setFocus()

        def moveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

        self.ui.headerContainer.mouseMoveEvent = moveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def validation_name(self):
        name = self.ui.nameFolderLineEdit.text().strip()
        if name and name != '..':
            self.accept()


class AddNSDialog(QDialog):
    def __init__(self):
        super().__init__()
        from interface import Ui_AddNSDialog

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ui = Ui_AddNSDialog()
        self.ui.setupUi(self)
        self.ui.nameLineEdit.enterPress.connect(self.validation_name)
        self.ui.okButton.clicked.connect(self.validation_name)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.nameLineEdit.setFocus()

        def moveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

        self.ui.headerContainer.mouseMoveEvent = moveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def validation_name(self):
        if self.ui.nameLineEdit.text().strip():
            self.accept()


class InfoBlockDialog(QDialog):
    def __init__(self, data):
        super().__init__()
        from interface import Ui_InfoBlockDialog
        from utils import amount_format
        from PyQt5.QtWidgets import QAbstractItemView, QFrame, QHeaderView

        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ui = Ui_InfoBlockDialog()
        self.ui.setupUi(self)

        self.ui.NumberBlockLabel.setText(str(data['number']))
        self.ui.HashBlockLabel.setText(data['hash_block'])
        self.ui.RecipientPoolAddressLabel.setText(data['recipient_pool'])
        self.ui.RecipientFogNodeAddressLabel.setText(data['recipient_fog_node'])
        self.ui.DateLabel.setText(datetime.fromtimestamp(data['date']).strftime('%Y-%m-%d %H:%M:%S'))
        self.ui.RecipientFogNodeAmountsLabel.setText(amount_format(data['amount_fog_node']))
        self.ui.RecipientPoolAmountLabel.setText(amount_format(data['amount_pool']))

        labels = ['Sender', 'Owner', 'Count ByteEx', 'Data', 'Date']  # Заголовки таблицы
        self.ui.TransactionTableWidget.setColumnCount(
            len(labels))  # Устанавливаем количество колонок по количеству заголовков
        self.ui.TransactionTableWidget.setHorizontalHeaderLabels(labels)  # Устанавливаем заголовки
        self.ui.TransactionTableWidget.verticalHeader().hide()  # Скрываем нумерацию рядов
        self.ui.TransactionTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет редактирования
        self.ui.TransactionTableWidget.setShowGrid(False)  # Скрываем сетку в таблице
        self.ui.TransactionTableWidget.setFrameStyle(QFrame.NoFrame)  # Скрываем рамку

        self.ui.TransactionTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.TransactionTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.TransactionTableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ui.TransactionTableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.ui.TransactionTableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.ui.TransactionTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.TransactionTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)

        self.ui.TransactionTableWidget.setRowCount(len(data['transactions']))
        i = 0
        for item in data['transactions']:
            self.ui.TransactionTableWidget.setItem(i, 0, QTableWidgetItem(item['sender']))
            self.ui.TransactionTableWidget.setItem(i, 1, QTableWidgetItem(item['owner']))
            self.ui.TransactionTableWidget.setItem(i, 2, QTableWidgetItem(amount_format(item['count'])))
            self.ui.TransactionTableWidget.setItem(i, 3, QTableWidgetItem(item['data']))
            self.ui.TransactionTableWidget.setItem(i, 4, QTableWidgetItem(
                datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')))
            i += 1

        self.ui.okButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)

        def moveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

        self.ui.headerContainer.mouseMoveEvent = moveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
