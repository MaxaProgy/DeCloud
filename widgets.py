import json
import os
import requests

from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QTableWidget, QDialog, QLabel, QWidget


# PushButton

class FogNodesButton(QPushButton):
    # Кнопка открытия управления fog nodes
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path('static/fog_nodes.png'))
        self.icon_2 = QIcon(get_path('static/fog_nodes2.png'))
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setToolTip('Окно управления fog nodes')
        self.setStyleSheet("""border-style: solid;""")

        self.setIcon(self.icon_1)

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)


class SettingsButton(QPushButton):
    # Кнопка Настроек
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path('static/settings.png'))
        self.icon_2 = QIcon(get_path('static/settings2.png'))
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setToolTip('Настройки приложения')
        self.setStyleSheet("""border-style: solid;""")

        self.setIcon(self.icon_1)

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)


class SearchButton(QPushButton):
    # Кнопка поиска по storages
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path('static/search.png'))
        self.icon_2 = QIcon(get_path('static/search2.png'))
        self.setIconSize(QSize(30, 30))
        self.setFixedSize(30, 30)
        self.setStyleSheet("""border-style: solid;""")
        self.setToolTip('Найти объект в сети')
        self.setIcon(self.icon_1)

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)


class SendRegistrationDomainNameButton(QPushButton):
    # Кнопка открытия диалогового окна для регистрации нового ns
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path('static/registration_ns.png'))
        self.icon_2 = QIcon(get_path('static/registration_ns2.png'))
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setStyleSheet("""border-style: solid;""")
        self.setToolTip('Регистрация доменного имени')
        self.setIcon(self.icon_1)

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)


class SendFileButton(QPushButton):
    # Кнопка открытия диалогового окна для загрузки файла в storages
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path('static/file.png'))
        self.icon_2 = QIcon(get_path('static/file2.png'))
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setStyleSheet("""border-style: solid;""")
        self.setToolTip('Загрузить файл в storage')
        self.setIcon(self.icon_1)

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)


class CreateDirectoryButton(QPushButton):
    # Кнопка открытия диалогового окна для создания новой директории
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path('static/dir.png'))
        self.icon_2 = QIcon(get_path('static/dir2.png'))
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setStyleSheet("""border-style: solid;""")
        self.setToolTip('Создать новую директорию в storage')
        self.setIcon(self.icon_1)

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)


class SendByteExButton(QPushButton):
    # Кнопка открытия диалогового окна для отправки byteEx
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path('static/send_byteEx.png'))
        self.icon_2 = QIcon(get_path('static/send_byteEx2.png'))
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setStyleSheet("""border-style: solid;""")
        self.setToolTip('Отправить byteEX')
        self.setIcon(self.icon_1)

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)


class CreateNodeButton(QPushButton):
    # Кнопка создания новгой fog node
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path('static/add_node.png'))
        self.icon_2 = QIcon(get_path('static/add_node2.png'))
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setStyleSheet("""border-style: solid;""")
        self.setToolTip('Создать новую fog node')
        self.setIcon(self.icon_1)

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)


class OpenPoolButton(QPushButton):
    # Кнопка открытия и создания пула
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize

        self.change_active_image('create')
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setStyleSheet("""border-style: solid;""")

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)

    def change_active_image(self, type):
        # Метод смены изображения
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path(f'static/{type}_pool.png'))
        self.icon_2 = QIcon(get_path(f'static/{type}_pool2.png'))
        self.setIcon(self.icon_1)

    def change_active_help(self, type, address):
        # Метод смены подсказки
        if type == 'open':
            self.setToolTip(f'Открыть Pool {address}')
        elif type == 'create':
            self.setToolTip(f'Создать Pool с адресом {address}')


class OpenClientStorageButton(QPushButton):
    # Кнопка открытия и создания client storage
    def __init__(self):
        super().__init__()
        from PyQt5.QtCore import QSize

        self.change_active_image('create')
        self.setIconSize(QSize(50, 50))
        self.setFixedSize(50, 50)
        self.setStyleSheet("""border-style: solid;""")

    def enterEvent(self, event):
        self.setIcon(self.icon_2)

    def leaveEvent(self, event):
        self.setIcon(self.icon_1)

    def change_active_image(self, type):
        # Метод смены изображения
        from PyQt5.QtGui import QIcon
        from utils import get_path

        self.icon_1 = QIcon(get_path(f'static/{type}_storage.png'))
        self.icon_2 = QIcon(get_path(f'static/{type}_storage2.png'))
        self.setIcon(self.icon_1)

    def change_active_help(self, type, address):
        # Метод смены подсказки
        if type == 'open':
            self.setToolTip(f'Открыть Storage {address}')
        elif type == 'create':
            self.setToolTip(f'Создать Storage с адресом {address}')


class ClientStoragesExplorer(QTableWidget):
    # Проводник client storage's, отображение файловой системы
    from PyQt5.QtCore import pyqtSignal
    update_dir = pyqtSignal(dict)
    message = pyqtSignal(str)

    def __init__(self, name=''):
        from threading import Thread
        from PyQt5.QtGui import QGuiApplication
        from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QFrame

        super().__init__()
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

        self.itemDoubleClicked.connect(self.open_object)  # По двойному нажатию открываем объект

        update_data_thread = Thread(target=self.update_data)  # Создание потока для обновления данный
        update_data_thread.start()

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

        if type_object == 'dir':
            if 'error' in response:
                self._last_response_hash = ''
                self.message.emit(response['error'])
                return
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
            if self._current_id_object != self.item(self.currentRow(), 0).text():  # Если введенный хапрос это файл
                self._last_response_hash = ''
                self.message.emit('ok')

    def update_data(self):
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
        import time

        while True:
            time.sleep(15)  # Каждые 15 секунд запрашиваем информацию об объекте
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

    def __init__(self, name: str):
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
        self._occupied_amount = 0  # Занятый баланс
        self.initUI()

    def initUI(self):
        from PyQt5.QtCore import Qt
        from utils import amount_format
        from PyQt5.QtWidgets import QLabel

        layout_balance = QHBoxLayout()
        layout_balance.addStretch(1)

        layout_v = QVBoxLayout()
        # --------- Widget all balance ---------
        layoutAllBalance = QHBoxLayout()
        self.labelAllBalanceClient = QLabel('Полный баланс: ')
        self.labelAmountClient = QLabel()
        layoutAllBalance.addWidget(self.labelAllBalanceClient)
        layoutAllBalance.addWidget(self.labelAmountClient)
        layout_v.addLayout(layoutAllBalance)
        # --------- Widget occupied balance ---------
        layoutOccupiedBalance = QHBoxLayout()
        self.labelOccupiedBalance = QLabel('Использовано: ')
        self.labelOccupiedAmount = QLabel(amount_format(0))
        layoutOccupiedBalance.addWidget(self.labelOccupiedBalance)
        layoutOccupiedBalance.addWidget(self.labelOccupiedAmount)

        layout_v.addLayout(layoutOccupiedBalance)
        layout_balance.addLayout(layout_v)
        self.addLayout(layout_balance)

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

        # --------- Widgets button ---------
        layout_menu = QVBoxLayout()
        self.createDirectoryButton = CreateDirectoryButton()
        self.createDirectoryButton.clicked.connect(self.create_dir)

        self.sendFileButton = SendFileButton()
        self.sendFileButton.clicked.connect(self.send_file)

        self.sendRegistrationDomainNameButton = SendRegistrationDomainNameButton()
        self.sendRegistrationDomainNameButton.clicked.connect(self.registration_domain_name)

        self.sendByteExButton = SendByteExButton()
        self.sendByteExButton.clicked.connect(self.send_byteEx)

        self.settingsButton = SettingsButton()
        self.settingsButton.clicked.connect(self.open_menu_settings)

        layout_menu.addLayout(layout_v)
        layout_menu.addWidget(self.createDirectoryButton)
        layout_menu.addWidget(self.sendFileButton)
        layout_menu.addWidget(self.sendRegistrationDomainNameButton)
        layout_menu.addWidget(self.sendByteExButton)
        layout_menu.addStretch(1)
        layout_menu.addWidget(self.settingsButton)
        layout.addLayout(layout_menu)
        self.addLayout(layout)

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
        from PyQt5.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self.clientStoragesExplorer, 'Registration domain name', 'Add domain name:')
        if ok:
            try:
                data = {'address': self._address, 'name': name}  # Отправляем запрос на регистрацию нового ns
                requests.post(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/registration_domain_name',
                              json=data)
            except:
                pass

    def send_byteEx(self):
        # Создаем модальное окно, обрабатываем получателя, отправителя, сумму перевода, отправляем
        Send_ByteEx(self._name).exec()

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

        self._occupied_amount = data['occupied']  # Обновляем использованный баланс
        self.labelOccupiedAmount.setText(amount_format(self._occupied_amount))

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

    def create_dir(self):
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
        from PyQt5.QtWidgets import QMessageBox, QInputDialog

        text, ok = QInputDialog.getText(self.clientStoragesExplorer, 'Input Dialog', 'Enter name directory:')
        if ok:
            if text == '..':
                QMessageBox.critical(self.clientStoragesExplorer, "Error", "Не корректное имя файла", QMessageBox.Ok)
            else:
                # Проверяем чтобы хватило места для создания директории
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
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
        from PyQt5.QtWidgets import QMessageBox, QFileDialog

        # Загрузка файла
        path = QFileDialog.getOpenFileName(self.clientStoragesExplorer, "Select a file...",
                                           None, filter="All files (*)")[0]
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

    def open_menu_settings(self):
        self.openSettings.emit()


class PoolWidget(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self._address_pool = None
        self.pool_balance = 0
        self._is_run = False  # Флаг на запущенл ли пул
        self.initUI()

    def initUI(self):
        from utils import amount_format, LoadJsonFile
        from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QFrame

        # --------- Widget all balance ---------
        layoutAllBalancePool = QHBoxLayout()
        self.labelAllBalancePool = QLabel('Полный баланс: ')
        self.labelAmountPool = QLabel(amount_format(0))
        layoutAllBalancePool.addStretch(1)
        layoutAllBalancePool.addWidget(self.labelAllBalancePool)
        layoutAllBalancePool.addWidget(self.labelAmountPool)
        self.addLayout(layoutAllBalancePool)

        # --------- Widget information blockchain ---------
        layout = QHBoxLayout()
        self.infoBlockchain = QTableWidget()
        labels = ['number block', 'recipient pool', 'amount pool', 'recipient fog node', 'amount fog node',
                  'transactions']  # Заголовки таблицы
        self.infoBlockchain.setColumnCount(len(labels))  # Устанавливаем количество колонок по количеству заголовков
        self.infoBlockchain.setHorizontalHeaderLabels(labels)  # Устанавливаем заголовки
        self.infoBlockchain.verticalHeader().hide()  # Скрываем нумерацию рядов
        self.infoBlockchain.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет редактирования
        self.infoBlockchain.setShowGrid(False)  # Скрываем сетку в таблице

        self.infoBlockchain.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.infoBlockchain.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)

        self.infoBlockchain.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.infoBlockchain.setSelectionMode(QAbstractItemView.SingleSelection)
        self.infoBlockchain.setFrameStyle(QFrame.NoFrame)  # Скрываем рамку

        # --------- Menu ---------
        layout_menu = QVBoxLayout()
        self.sendByteExButton = SendByteExButton()
        self.sendByteExButton.clicked.connect(self.send_byteEx)
        layout_menu.addWidget(self.sendByteExButton)
        layout_menu.addStretch(1)

        layout.addWidget(self.infoBlockchain)
        layout.addLayout(layout_menu)
        self.addLayout(layout)

        private_key = LoadJsonFile('data/pool/key').as_string()
        if private_key:  # В файле всегда 1 ключ, если он есть, значит пул уже был создан, поэтому запускаем пул
            self.start_pool(private_key)

    def is_run(self):
        return self._is_run

    def send_byteEx(self):
        # Создаем модальное окно, обрабатываем получателя, отправителя, сумму перевода, отправляем
        Send_ByteEx(self._address_pool).exec()

    def start_pool(self, private_key):
        from pool import Pool
        from wallet import Wallet

        try:
            self.pool = Pool(private_key)
            self.pool.start()
            self._address_pool = Wallet(private_key).address
            self._is_run = True
        except Exception as e:
            print(e)

    def change_balance_pool(self, amount):
        from utils import amount_format

        self.pool_balance = amount  # Обновляем полный баланс пула
        self.labelAmountPool.setText(amount_format(amount))


class FogNodesWidget(QHBoxLayout):
    from PyQt5.QtCore import pyqtSignal

    openPool = pyqtSignal(str)  # Сигнал на открытие вкладки пула и создания/запуска
    changeBalanceClientsStorage = pyqtSignal(str, int)  # Сигнал на изменение баланса клиента
    createClientStorage = pyqtSignal(str)  # Сигнал на создание клиента
    changeBalancePool = pyqtSignal(int)  # Сигнал на изменение баланса пула
    openSettings = pyqtSignal()

    def __init__(self):
        super().__init__()
        from PyQt5.QtGui import QGuiApplication

        self.clipboard = QGuiApplication.clipboard()  # Буфер обмена
        self.initUI()

    def initUI(self):
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        from fog_nodes_manager import ManagerFogNodes
        from wallet import Wallet
        from utils import LoadJsonFile
        from variables import POOL_BACKGROUND_COLOR, CLIENT_STORAGE_FOREGROUND_COLOR
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
            if self._address_pool == address:  # Если node являестся пулом, то меняем стиль
                self.fogNodesTableWidget.item(row, 0).setBackground(QColor(POOL_BACKGROUND_COLOR))
            row += 1

        self.fogNodesTableWidget.setSortingEnabled(True)  # Устанавливаем сортировку
        self.fogNodesTableWidget.sortByColumn(0, Qt.AscendingOrder)
        self.fogNodesTableWidget.setCurrentCell(0, 0)

        # Создаем контекстное меню
        self.fogNodesTableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fogNodesTableWidget.customContextMenuRequested.connect(self._context_menu_open)

        self.fogNodesTableWidget.cellClicked.connect(self.current_item_change)  # Обработка на нажатие на ячейку
        self.fogNodesTableWidget.setStyleSheet('''QTableWidget::item:selected {
                                                    background: #ece9d8;
                                                    color: blue;
                                                 }''')  # Стили на активную ячейку

        self.mfn = ManagerFogNodes()
        self.mfn.load_fog_nodes('data/fog_nodes/key')
        self.mfn.on_change_balance = self.on_change_balance
        self.mfn.on_change_state = self.on_change_state

        # --------- Menu ---------
        layout = QVBoxLayout()
        self.createNodeButton = CreateNodeButton()
        self.createNodeButton.clicked.connect(self.create_node)

        self.openPoolButton = OpenPoolButton()
        self.openPoolButton.clicked.connect(self.create_and_open_pool)
        self.openPoolButton.setVisible(not self._address_pool and self.fogNodesTableWidget.rowCount() > 0)

        self.sendByteExButton = SendByteExButton()
        self.sendByteExButton.clicked.connect(self.send_byteEx)

        self.openClientStorageButton = OpenClientStorageButton()
        self.openClientStorageButton.clicked.connect(self.create_client_storage)
        self.openClientStorageButton.setVisible(self.fogNodesTableWidget.rowCount() > 0)

        self.settingsButton = SettingsButton()
        self.settingsButton.clicked.connect(self.open_menu_settings)

        layout.addWidget(self.createNodeButton)
        layout.addWidget(self.openPoolButton)
        layout.addWidget(self.openClientStorageButton)
        layout.addWidget(self.sendByteExButton)
        layout.addStretch(1)
        layout.addWidget(self.settingsButton)
        self.addWidget(self.fogNodesTableWidget)
        self.addSpacing(10)
        self.addLayout(layout)

    def open_menu_settings(self):
        self.openSettings.emit()

    def current_item_change(self, row, column):
        from variables import POOL_BACKGROUND_COLOR, CLIENT_STORAGE_FOREGROUND_COLOR

        self.openPoolButton.setVisible(
            not bool(self._address_pool) or
            self.fogNodesTableWidget.item(row, 0).background().color().name() == POOL_BACKGROUND_COLOR)
        if not self._address_pool:  # Если пул еще не создан, то изменяем подсказку на кнопке создания пула
            self.openPoolButton.change_active_help('create', self.fogNodesTableWidget.item(row, 4).text())
        # Изменяем подсказку и изображение кнопки
        if self.fogNodesTableWidget.item(row, 0).foreground().color().name() == CLIENT_STORAGE_FOREGROUND_COLOR:
            self.openClientStorageButton.change_active_image('open')
            self.openClientStorageButton.change_active_help('open', self.fogNodesTableWidget.item(row, 4).text())
        else:
            self.openClientStorageButton.change_active_image('create')
            self.openClientStorageButton.change_active_help('create', self.fogNodesTableWidget.item(row, 4).text())

    def create_and_open_pool(self):
        from PyQt5.QtGui import QColor
        from wallet import Wallet
        from utils import LoadJsonFile
        from variables import POOL_BACKGROUND_COLOR

        self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).setBackground(
            QColor(POOL_BACKGROUND_COLOR))  # Изменение стиля
        self.openPoolButton.change_active_image('open')  # Изменение стиля кнопки с create -> open
        self.openPoolButton.change_active_help('open',
                                               self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(),
                                                                             4).text())

        if not self._address_pool:  # Если адрес пустой, значит пул еще не был создан
            # Получаем приватный ключ текушей ячеки, Записываем адрес пула
            address = self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 4).text()
            for item in LoadJsonFile('data/fog_nodes/key').as_list():
                if Wallet(item).address == address:
                    self._address_pool = address
                    self.openPool.emit(item)
                    return
        # Иначе пул уже существует, забираем ключь из файла пула
        self.openPool.emit(LoadJsonFile('data/pool/key').as_string())

    def current_fog_node(self):
        # Возвращаем имя текущего ряда, если есть хотя бы 1 ряд, иначе ''
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
        self.openPoolButton.setVisible(not self._address_pool)
        self.openClientStorageButton.setVisible(True)

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

        self.openClientStorageButton.change_active_image('open')  # Изменение стилей кнопки с create -> open
        self.openClientStorageButton.change_active_help('open', self.fogNodesTableWidget.item(
            self.fogNodesTableWidget.currentRow(), 4).text())


        for key in LoadJsonFile('data/fog_nodes/key').as_list():
            if Wallet(key).address == self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 4).text():
                if key not in LoadJsonFile('data/clients_manager/key').as_list():
                    Wallet(key).save_private_key('data/clients_manager/key')
                    break

        self.createClientStorage.emit(self.current_fog_node())  # Отправляем сигнал на открытие вкладки клиента
        self.fogNodesTableWidget.item(self.fogNodesTableWidget.currentRow(), 0).setForeground(
            QColor(CLIENT_STORAGE_FOREGROUND_COLOR))  # Изменение стилейв таблице fog nodes


class Send_ByteEx(QDialog):
    def __init__(self, sender: str):
        super().__init__()
        # Модальное окно для отправки byteEx
        from PyQt5.QtGui import QIntValidator
        from PyQt5.QtWidgets import QGridLayout, QDialogButtonBox, QLabel, QLineEdit

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
        self.lineEditAmount.setValidator(QIntValidator(0, 10000000, self))
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
        from variables import PORT_DISPATCHER_CLIENTS_MANAGER, DNS_NAME
        from PyQt5.QtWidgets import QMessageBox

        try:  # Получаем баланс, которым может воспользываться пользователь
            response = requests.get(f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/'
                                    f'api/get_free_balance/{self.lineEditSender.text()}').json()
        except:
            QMessageBox.critical(self, "Error", 'Error connection', QMessageBox.Ok)
            return
        if response['status'] == 100:
            QMessageBox.critical(self, "Error", response['status_text'], QMessageBox.Ok)
            return

        if self.lineEditAmount.text() == '':  # Валидация на пустое поле суммы
            self.lineEditAmount.setText('0')

        amount = int(self.lineEditAmount.text())
        if amount <= response['amount_free_balance']:  # Валидация на отправляемую сумму
            transaction = {'sender': self.lineEditSender.text(), 'owner': self.lineEditOwner.text(),
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
            QMessageBox.critical(self, "Error", f"{self.lineEditOwner.text()} don't have enough byteEx", QMessageBox.Ok)


class SearchClientStorage(QVBoxLayout):
    from PyQt5.QtCore import pyqtSignal
    changeSearchState = pyqtSignal(str)
    openFogNodes = pyqtSignal()
    openPool = pyqtSignal()
    createClientStorage = pyqtSignal()
    openClientStorages = pyqtSignal()

    class Menu(QVBoxLayout):
        def __init__(self, parent):
            super().__init__()
            from utils import  LoadJsonFile
            from wallet import Wallet

            self.parent = parent
            self.addStretch(1)
            layout = QHBoxLayout()
            layout.addStretch(1)
            self.widgets = []
            self.widgets.append(FogNodesButton())
            self.widgets[-1].clicked.connect(self.open_fog_nodes)

            self.widgets.append(OpenClientStorageButton())
            self.widgets[-1].clicked.connect(self.create_client_storage)

            private_key = LoadJsonFile('data/pool/key').as_string()
            if private_key:
                self.widgets.append(OpenPoolButton())
                self.widgets[-1].change_active_image('open')
                self.widgets[-1].change_active_help('open', Wallet(private_key).address)
                self.widgets[-1].clicked.connect(self.open_pool(private_key))

            self.widgets.append(OpenClientStorageButton())
            self.widgets[-1].change_active_image('open')
            self.widgets[-1].change_active_help('open', '')
            self.widgets[-1].clicked.connect(self.open_client_storages)

            [layout.addWidget(item) for item in self.widgets]

            layout.addStretch(1)
            self.addLayout(layout)
            self.addStretch(1)

        def open_client_storages(self):
            self.parent.openClientStorages.emit()

        def create_client_storage(self):
            self.parent.createClientStorage.emit()

        def open_fog_nodes(self):
            self.parent.openFogNodes.emit()

        def open_pool(self, private_key):
            self.parent.openPool.emit(private_key)

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

    def __init__(self):
        super().__init__()
        self.initUI()
        self.message = None

    def initUI(self):
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        from PyQt5.QtWidgets import QLineEdit, QHBoxLayout

        # ------------ Widgets search ------------
        layout = QHBoxLayout()
        self.search = QLineEdit()
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

        layout.addWidget(self.search, stretch=5)
        self.searchButton = SearchButton()
        layout.addWidget(self.searchButton)
        self.addLayout(layout)
        self.searchButton.clicked.connect(self.search_path)

        # ------------ Widgets Menu ------------
        self.menu = self.Menu(self)
        self.addLayout(self.menu)
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

        if path == '':
            if not self.menu:
                self.menu = self.Menu(self)
                self.addLayout(self.menu)
            self.clientStoragesExplorer.hide()
        else:
            if self.menu:
                self.menu.fogNodesButton.hide()
                self.removeItem(self.menu)
                self.menu = None

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
    from PyQt5.QtCore import pyqtSignal
    selectedClientStorage = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Модальное окно для отправки byteEx
        from PyQt5.QtWidgets import QListWidget
        from utils import LoadJsonFile
        from wallet import Wallet

        self.resize(500, 200)

        layout = QVBoxLayout()
        self.allClientStoragesListWidget = QListWidget()
        layout.addWidget(self.allClientStoragesListWidget)
        for key in LoadJsonFile('data/clients_manager/key').as_list():
            self.allClientStoragesListWidget.addItem(Wallet(key).address)
        self.allClientStoragesListWidget.doubleClicked.connect(self.selected_client_storage)

        self.setLayout(layout)
        self.setWindowTitle("All Client Storages")
        self.exec_()

    def selected_client_storage(self):
        self.selectedClientStorage.emit(self.allClientStoragesListWidget.currentItem().text())
        self.destroy()

