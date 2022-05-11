from PyQt5.QtWidgets import QMainWindow, QFrame, QSystemTrayIcon, QMenu, QAction, QHeaderView
from clients_manager import DispatcherClientsManager
from interface import *
from utils import SaveJsonFile, LoadJsonFile
from variables import POOL_ROOT_EXTERNAL_IP, PORT_DISPATCHER_CLIENTS_MANAGER
import resources_rc


class AppClient(QMainWindow):
    def __init__(self, port_pool, port_cm, port_fn):
        super().__init__()

        from utils import exists_path
        from PyQt5.QtWidgets import QLabel, QToolButton, QTabBar
        from PyQt5.QtGui import QIcon
        from PyQt5.QtCore import Qt
        from widgets import FogNodesWidget, PoolWidget, SearchClientStorage

        self.dispatcher = DispatcherClientsManager(PORT_DISPATCHER_CLIENTS_MANAGER)
        self.dispatcher.start()

        self.port_pool = port_pool
        self.port_cm = port_cm
        self.port_fn = port_fn

        self.setWindowTitle("DeCloud")
        self.setWindowIcon(QIcon(':/images/icon.png'))
        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.activated.connect(self.on_click_tray_icon)
        self.tray_icon.setIcon(QIcon(':/images/icon.png'))
        tray_menu = QMenu()
        tray_menu.triggered.connect(self.show)
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabWidget.currentChanged.connect(self.change_tab)
        self.ui.tabWidget.tabCloseRequested.connect(self.closeTab)

        self.fogNodesWidget = FogNodesWidget(self)  # Widget Fog Nodes
        self.poolWidget = PoolWidget(self)  # Widget Pool

        if exists_path('data/state_app'):
            # При надичии файла state_app загружаем предыдущее состояние приложения
            self.load_state_app()
        else:
            # Иначе создаем стартовое состояние приложения
            tabSearch = QFrame()
            search = SearchClientStorage(self)
            search.changeSearchState.connect(self.save_state_app)
            tabSearch.setLayout(search)
            self.ui.tabWidget.addTab(tabSearch, 'New tab')

        # Добавление вкладки с кнопкой создания страницы поиска
        self.ui.tabWidget.addTab(QLabel(""), '')
        self.addTabButton = QToolButton()
        self.addTabButton.setStyleSheet(""" QToolButton {
                                            background-repeat:none;
                                            background-position: center;
                                            background-image: url(:/icons/icons/plus.svg);
                                            }
                                            QToolButton:hover {
                                            background-image: url(:/icons/icons/plus(1).svg);
                                            }
        
        """)
        self.addTabButton.setMinimumSize(20,20)
        self.addTabButton.clicked.connect(self.new_window)
        self.ui.tabWidget.tabBar().setTabButton(self.ui.tabWidget.count() - 1, QTabBar.RightSide, self.addTabButton)
        self.ui.tabWidget.setTabEnabled(self.ui.tabWidget.count() - 1, False)  # Неактивное состояние вкладки

        self.ui.allFogNodesButton.clicked.connect(self.open_tab_fog_nodes)
        self.ui.allStoragesButton.clicked.connect(self.all_client_storages)
        self.ui.openClientStorageButton.clicked.connect(self.create_client_storage)
        self.ui.sendByteExButton.clicked.connect(self.send_byteEx)
        self.ui.createPoolButton.clicked.connect(self.create_pool)
        self.ui.openPoolButton.clicked.connect(self.open_pool)
        self.ui.openToolsButton.clicked.connect(self.slide_left_tools_menu)
        self.ui.informationButton.clicked.connect(self.open_center_tools_menu)
        self.ui.settingsButton.clicked.connect(self.open_center_tools_menu)
        self.ui.closeCenterToolsButton.clicked.connect(self.close_center_tools_menu)
        self.ui.submitButton.clicked.connect(self.submit_settings)
        self.ui.addFogNodeButton.clicked.connect(self.fogNodesWidget.create_node)

        self.ui.restoreButton.clicked.connect(self.restore_or_maximize_window)
        self.ui.minimizeButton.clicked.connect(self.showMinimized)
        self.ui.closeButton.clicked.connect(self.hide)

        def moveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

        self.ui.headerContainer.mouseMoveEvent = moveWindow

    def on_click_tray_icon(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()

    def information(self):
        pass

    def submit_settings(self):
        self.close_center_tools_menu()

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def close_center_tools_menu(self):
        from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
        width = self.ui.centerToolsContainer.width()
        if width == 250:
            self.animation = QPropertyAnimation(self.ui.centerToolsContainer, b'minimumWidth')
            self.animation.setDuration(250)
            self.animation.setStartValue(width)
            self.animation.setEndValue(0)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

    def open_center_tools_menu(self):
        from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
        width = self.ui.centerToolsContainer.width()
        if self.sender().text().strip() == 'Information':
            if width == 250 and self.ui.stackedWidget.currentWidget() == self.ui.pageInformation:
                self.close_center_tools_menu()
            else:
                self.ui.stackedWidget.setCurrentWidget(self.ui.pageInformation)
        else:
            if width == 250 and self.ui.stackedWidget.currentWidget() == self.ui.pageSettings:
                self.close_center_tools_menu()
            else:
                self.ui.stackedWidget.setCurrentWidget(self.ui.pageSettings)

        if width == 0:
            self.ui.poolPortlineEdit.setText(str(self.port_pool))
            self.ui.CMPortlineEdit.setText(str(self.port_cm))
            self.ui.FNPortlineEdit.setText(str(self.port_fn))
            self.ui.rootIPlineEdit.setText(str(POOL_ROOT_EXTERNAL_IP))
            new_width = 250
            self.animation = QPropertyAnimation(self.ui.centerToolsContainer, b'minimumWidth')
            self.animation.setDuration(250)
            self.animation.setStartValue(width)
            self.animation.setEndValue(new_width)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

    def slide_left_tools_menu(self):
        from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

        width = self.ui.leftToolsSubContainer.width()
        if width == 55:
            new_width = 200
        else:
            new_width = 55
        self.animation = QPropertyAnimation(self.ui.leftToolsSubContainer, b'minimumWidth')
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    def restore_or_maximize_window(self):
        from PyQt5.QtGui import QIcon
        if self.isMaximized():
            self.showNormal()
            self.ui.restoreButton.setIcon(QIcon(u':/icons/icons/square.svg'))
        else:
            self.showMaximized()
            self.ui.restoreButton.setIcon(QIcon(u':/icons/icons/copy.svg'))

        if self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Pool':
            self.poolWidget.infoBlockchain.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.poolWidget.infoBlockchain.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.poolWidget.infoBlockchain.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            self.poolWidget.infoBlockchain.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            self.poolWidget.infoBlockchain.hide()
            self.poolWidget.infoBlockchain.show()

    def closeTab(self, ind):
        # Метод закрывает вкладку под номером ind
        self.ui.tabWidget.removeTab(ind)
        self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 2)
        if self.ui.tabWidget.count() == 1:
            self.new_window()
        self.save_state_app()

    def closeEvent(self, event):
        from variables import DNS_NAME, PORT_DISPATCHER_CLIENTS_MANAGER
        import requests

        close = QtWidgets.QMessageBox.question(self, "QUIT", "Are you sure want to exit DeCloud?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            self.hide()
            self.fogNodesWidget.mfn.close()
            self.poolWidget.stop()
            self.dispatcher.stop()
            self.tray_icon.hide()
            exit()

    def send_byteEx(self):
        from widgets import Send_ByteEx
        current_tab = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if current_tab == 'Pool':
            sender = self.poolWidget._address_pool
        elif current_tab == 'Fog Nodes':
            sender = self.fogNodesWidget.current_fog_node()
        else:
            sender = current_tab
        Send_ByteEx(sender).exec()

    def _get_index_name_tab(self, address):
        # Функция получения индекса по адресу во вкладках
        for i in range(self.ui.tabWidget.count()):
            if address == self.ui.tabWidget.tabText(i):
                return i
        return -1  # Если такой вкладки нет

    def open_pool(self):
        index = self._get_index_name_tab('Pool')
        if index > -1:  # Если индекс != -1, то вкладка Pool существует
            self.ui.tabWidget.setCurrentIndex(index)  # Переходим на существующую вкладку
        else:
            tabPool = QFrame()  # Иначе создаем вкладку Pool
            tabPool.setLayout(self.poolWidget)

            self.ui.tabWidget.insertTab(self.ui.tabWidget.count() - 1, tabPool, "Pool")
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 2)  # Открываем вкладку
            self.save_state_app()  # Сохраняем новое состояние приложения

    def create_pool(self):
        if not self.poolWidget._address_pool:
            private_key = self.fogNodesWidget.create_pool()
            self.poolWidget.start_pool(private_key)
            self.open_pool()

    def save_state_app(self):
        from widgets import SearchClientStorage

        new_data_state = []
        for i in range(self.ui.tabWidget.count()-1):
            name_tab = self.ui.tabWidget.tabText(i)
            if name_tab == 'New tab':  # Если вкладка New tab, то сохраняем и текст из строки поиска
                new_data_state.append(
                    {'New tab': self.ui.tabWidget.widget(i).findChild(SearchClientStorage).search.text()})
            else:
                # Иначе сохраняем просто имя вкладки
                new_data_state.append(name_tab)
        SaveJsonFile('data/state_app', {'list_tab': new_data_state})

    def load_state_app(self):
        from wallet import Wallet
        import requests
        from widgets import SearchClientStorage, ClientStorageWidget
        from variables import DNS_NAME, PORT_DISPATCHER_CLIENTS_MANAGER

        last_state = LoadJsonFile('data/state_app').as_dict()  # Загружаем предыдущий state
        # И адреса client storages
        addresses_client = [Wallet(key).address for key in LoadJsonFile('data/clients_manager/key').as_list()]
        for name_tab in last_state['list_tab']:  # Восстанавливаем вкладки
            if type(name_tab) == dict:  # Если тип dict, то вкладка - New tab
                tabSearch = QFrame()
                search = SearchClientStorage(self)
                search.clientStoragesExplorer.change_path(name_tab['New tab'])  # Отображаем строку поиска из state
                search.changeSearchState.connect(self.save_state_app)
                tabSearch.setLayout(search)
                self.ui.tabWidget.addTab(tabSearch, 'New tab')

            elif name_tab == 'Pool':
                tabPool = QFrame()
                tabPool.setLayout(self.poolWidget)
                self.ui.tabWidget.addTab(tabPool, "Pool")

            elif name_tab == 'Fog Nodes':
                # Создание вкладки Fog node
                tabFogNodes = QFrame()
                self.fogNodesWidget.changeBalanceClientsStorage.connect(self.change_balance_clients_storage)
                self.fogNodesWidget.changeBalancePool.connect(self.change_balance_pool)
                tabFogNodes.setLayout(self.fogNodesWidget)
                self.ui.tabWidget.addTab(tabFogNodes, "Fog Nodes")

            else:
                try:  # Адрес клиента
                    address = requests.get(
                        f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/address_normal/{name_tab}').json()
                except:
                    print(f'Клиента с именем {name_tab} не существует в сети')
                    continue
                if address in addresses_client:  # вкладка - client storage
                    tabClientStorages = QFrame()
                    clientStorageWidget = ClientStorageWidget(self, name_tab)
                    clientStorageWidget.changeNs.connect(self.change_ns_client_storage)
                    # clientStorageWidget.change_balance(int(self.fogNodesWidget.fogNochange_address_client_storagedesTableWidget.item(
                    # self.fogNodesWidget.fogNodesTableWidget.currentRow(), 3).text()))
                    tabClientStorages.setLayout(clientStorageWidget)
                    self.ui.tabWidget.addTab(tabClientStorages, name_tab)

    def open_tab_fog_nodes(self):
        # Создание вкладки Fog node
        index = self._get_index_name_tab('Fog Nodes')
        if index > -1:
            self.ui.tabWidget.setCurrentIndex(index)
        else:
            tabFogNodes = QFrame()
            self.fogNodesWidget.changeBalanceClientsStorage.connect(self.change_balance_clients_storage)
            self.fogNodesWidget.changeBalancePool.connect(self.change_balance_pool)
            tabFogNodes.setLayout(self.fogNodesWidget)
            self.ui.tabWidget.insertTab(self.ui.tabWidget.count() - 1, tabFogNodes, "Fog Nodes")
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 2)
            self.save_state_app()

    def new_window(self):
        from widgets import SearchClientStorage
        # Добавление новой вкладка поиска по storages
        tabSearch = QFrame()
        search = SearchClientStorage(self)
        search.changeSearchState.connect(self.save_state_app)
        tabSearch.setLayout(search)

        self.ui.tabWidget.insertTab(self.ui.tabWidget.count() - 1, tabSearch, 'New tab')
        self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 2)  # Открытие вкладки
        self.save_state_app()

    # -------------- Обработчики сигналов ClientStorageWidget --------------
    def change_ns_client_storage(self, ns, normal_address):
        from PyQt5.QtGui import QColor
        from widgets import ClientStorageWidget
        from PyQt5.QtWidgets import QTableWidgetItem
        from variables import POOL_BACKGROUND_COLOR, BACKGROUND_COLOR
        # ns - имя storage, отображаемое в приложении, на которое нужно заменить старое имя
        # normal_address - реальный адрес storage

        # Устанавливаем новгое имя fog node storage's
        for i in range(self.fogNodesWidget.fogNodesTableWidget.rowCount()):
            # Если normal_address совпадает с адресом fog node, то эта fog node и есть этот storage,
            # следовательно заменяем отображаемое имя node
            if self.fogNodesWidget.fogNodesTableWidget.item(i, 4).text() == normal_address:
                # Получаем стили ячейки перед изменением, для их повторного установления
                color_background = self.fogNodesWidget.fogNodesTableWidget.item(i, 0).background().color().name()
                if color_background != POOL_BACKGROUND_COLOR:
                    color_background = BACKGROUND_COLOR
                color_foreground = self.fogNodesWidget.fogNodesTableWidget.item(i, 0).foreground().color()
                # Отмена сортировки, чтобы данные ячейки не сместились после записи
                self.fogNodesWidget.fogNodesTableWidget.setSortingEnabled(False)
                self.fogNodesWidget.fogNodesTableWidget.setItem(i, 0, QTableWidgetItem(ns))  # Запись новго имени

                # Установление стилей
                self.fogNodesWidget.fogNodesTableWidget.item(i, 0).setBackground(QColor(color_background))
                self.fogNodesWidget.fogNodesTableWidget.item(i, 0).setForeground(color_foreground)
                self.fogNodesWidget.fogNodesTableWidget.setSortingEnabled(True)  # Возвращение сортировки
                break

        # Устанавливаем новое имя на вкладке storage
        self.ui.tabWidget.setTabText(self.ui.tabWidget.currentIndex(),
                                     ns)  # Текущая вкладка - вкладка storage, имя которого изменяем
        # Изменяем адрес в explorer, для отображения короткого пути к объектам storage's

        # ------ Пример: -------
        # Путь к объекту storagre's через адрес  <адрес>/<id объекта>:
        # 521Fceb7C3b8E30aa200ACa5D6672A2b79Ad04b9/131061ca59a8adb856713e7f4de6b421efd1ca9ef96eac2a5f8d66e339084405
        # Путь к объекту storagre's через ns <ns>/<id объекта>:
        # PetrIvanov/131061ca59a8adb856713e7f4de6b421efd1ca9ef96eac2a5f8d66e339084405

        self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex()).findChild(
            ClientStorageWidget).clientStoragesExplorer.change_name(ns)

    def create_client_storage(self):
        current_tab = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if current_tab == 'New tab':
            from wallet import Wallet
            wallet = Wallet()
            wallet.save_private_key('data/clients_manager/key')
            address = wallet.address
        elif current_tab == 'Fog Nodes':
            address = self.fogNodesWidget.create_client_storage()

        self.open_client_storage(address)

    def all_client_storages(self):
        from widgets import AllClientStorages
        from PyQt5.QtWidgets import QDialog
        all_client_storages = AllClientStorages()
        if all_client_storages.exec_() ==  QDialog.Accepted:
            self.open_client_storage(all_client_storages.ui.listWidget.currentItem().text())

    # -------------- Обработчики сигналов FogNodesWidget --------------

    def open_client_storage(self, address):
        from widgets import ClientStorageWidget

        index = self._get_index_name_tab(address)
        if index > -1:  # Если индекс != -1, то вкладка с названием address существует
            self.ui.tabWidget.setCurrentIndex(index)  # Переходим на существующую вкладку
        else:
            # Cоздаем вкладку
            tabClientStorages = QFrame()
            clientStorageWidget = ClientStorageWidget(self, address)
            clientStorageWidget.changeNs.connect(self.change_ns_client_storage)
            # Отображем полный баланс во вкладке
            if self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Fog Nodes':
                clientStorageWidget.change_balance(int(self.fogNodesWidget.fogNodesTableWidget.item(
                    self.fogNodesWidget.fogNodesTableWidget.currentRow(), 3).text()))
            tabClientStorages.setLayout(clientStorageWidget)

            self.ui.tabWidget.insertTab(self.ui.tabWidget.count() - 1, tabClientStorages, address)
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 2)  # Открываем вкладку
            self.save_state_app()  # Сохраняем новое состояние приложения

    def change_balance_clients_storage(self, name, amount):
        from widgets import ClientStorageWidget
        # Изменение полного баланса storage
        for i in range(self.ui.tabWidget.count()):
            if self.ui.tabWidget.tabText(i) == name:  # Если имя вкладки совпадает с name,
                # отправляем запрос на изменение текщего баланса
                self.ui.tabWidget.widget(i).findChild(ClientStorageWidget).change_balance(amount)

    def change_balance_pool(self, amount):
        # Отправляем запрос на изменение pool баланса
        self.poolWidget.change_balance_pool(amount)

    def change_tab(self, index):
        if self.ui.tabWidget.tabText(index) == 'Pool':
            self.ui.sendByteExButton.show()
            self.ui.allFogNodesButton.show()

            self.ui.addFogNodeButton.hide()
            self.ui.openPoolButton.hide()
            self.ui.createPoolButton.hide()
            self.ui.openClientStorageButton.hide()
            self.ui.createFolderButton.hide()
            self.ui.sendFileButton.hide()
            self.ui.addNSButton.hide()
        elif self.ui.tabWidget.tabText(index) == 'Fog Nodes':
            if not self.fogNodesWidget._address_pool and self.fogNodesWidget.fogNodesTableWidget.rowCount() > 0:
                self.ui.createPoolButton.show()
                self.ui.openPoolButton.hide()
            elif self.fogNodesWidget._address_pool:
                self.ui.createPoolButton.hide()
                self.ui.openPoolButton.show()
            else:
                self.ui.createPoolButton.hide()
                self.ui.openPoolButton.hide()

            self.ui.openClientStorageButton.setVisible(self.fogNodesWidget.fogNodesTableWidget.rowCount() > 0)

            self.ui.addFogNodeButton.show()
            self.ui.sendByteExButton.show()

            self.ui.allFogNodesButton.hide()
            self.ui.createFolderButton.hide()
            self.ui.sendFileButton.hide()
            self.ui.addNSButton.hide()
        elif self.ui.tabWidget.tabText(index) == 'New tab':
            self.ui.allFogNodesButton.show()
            if LoadJsonFile('data/pool/key').as_string():
                self.ui.openPoolButton.show()
            else:
                self.ui.openPoolButton.hide()
            self.ui.createPoolButton.hide()
            self.ui.addFogNodeButton.hide()
            self.ui.sendByteExButton.hide()
            self.ui.openClientStorageButton.show()
            self.ui.openClientStorageButton.setText('    Create Client Storage')
            self.ui.createFolderButton.hide()
            self.ui.sendFileButton.hide()
            self.ui.addNSButton.hide()
        else:
            self.ui.createFolderButton.show()
            self.ui.sendFileButton.show()
            self.ui.addNSButton.show()
            self.ui.sendByteExButton.show()
            self.ui.allFogNodesButton.show()
            if LoadJsonFile('data/pool/key').as_string():
                self.ui.openPoolButton.show()
            else:
                self.ui.openPoolButton.hide()
            self.ui.createPoolButton.hide()
            self.ui.addFogNodeButton.hide()

            self.ui.openClientStorageButton.hide()
