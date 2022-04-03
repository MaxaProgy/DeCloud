from PyQt5.QtWidgets import QMainWindow, QFrame
from utils import LoadJsonFile, SaveJsonFile


class AppClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self._address_pool = LoadJsonFile('data/pool/key').as_string()  # Загружаем адрес пул

        self.setWindowTitle("DeCloud")
        from PyQt5.QtWidgets import QDesktopWidget
        from PyQt5.QtGui import QIcon
        from utils import get_path
        self.geometry = QDesktopWidget().availableGeometry()

        self.setWindowIcon(QIcon(get_path('static/icon.png')))
        try:  # Отображение иконки на панели приложений
            from PyQt5.QtWinExtras import QtWin
            QtWin.setCurrentProcessExplicitAppUserModelID(get_path('static/icon.png'))
        except ImportError:
            pass
        self.setGeometry(1000, 1000, 1000, 800)
        self.move(500, 100)
        self.initUI()

    def initUI(self):
        from PyQt5.QtWidgets import QLabel, QToolButton, QTabBar, QTabWidget
        from widgets import FogNodesWidget, PoolWidget, SearchClientStorage
        from utils import exists_path

        self.fogNodesWidget = FogNodesWidget()  # Widget Fog Nodes
        self.poolWidget = PoolWidget()  # Widget Pool

        self.tab = QTabWidget()  # Tab app
        self.tab.setTabsClosable(True)  # Добавление кнопок закрытия вкладок
        self.tab.tabCloseRequested.connect(self.closeTab)  # Обработка зарытия вкладки
        self.tab.setMovable(True)  # Разрешение на перемещение вкладок
        self.setCentralWidget(self.tab)

        if exists_path('data/clients_manager/state_app'):
            # При надичии файла state_app загружаем предыдущее состояние приложения
            self.load_state_app()
        else:
            # Иначе создаем стартовое состояние приложения
            tabSearch = QFrame()
            search = SearchClientStorage()
            search.changeSearchState.connect(self.save_state_app)
            search.openFogNodes.connect(self.open_tab_fog_nodes)
            search.createClientStorage.connect(self.create_client_storage)
            search.openClientStorages.connect(self.open_client_storages)
            search.openPool.connect(self.open_pool)
            tabSearch.setLayout(search)
            self.tab.addTab(tabSearch, 'New tab')

        # Добавление вкладки с кнопкой создания страницы поиска

        self.tab.addTab(QLabel(""), '')
        self.addTabButton = QToolButton()
        self.addTabButton.setText('+')
        self.addTabButton.clicked.connect(self.new_window)
        self.tab.tabBar().setTabButton(self.tab.count() - 1, QTabBar.RightSide, self.addTabButton)
        self.tab.setTabEnabled(self.tab.count() - 1, False)  # Неактивное состояние вкладки

    def closeTab(self, ind):
        # Метод закрывает вкладку под номером ind
        self.tab.removeTab(ind)
        self.tab.setCurrentIndex(self.tab.count() - 2)
        if self.tab.count() == 1:
            self.new_window()

    def closeEvent(self, event):
        self.showMinimized()
        event.ignore()

    def _get_index_name_tab(self, address):
        # Функция получения индекса по адресу во вкладках
        for i in range(self.tab.count()):
            if address == self.tab.tabText(i):
                return i
        return -1  # Если такой вкладки нет

    def save_state_app(self):
        from widgets import SearchClientStorage

        new_data_state = []
        for i in range(self.tab.count()):
            name_tab = self.tab.tabText(i)
            if name_tab == 'New tab':  # Если вкладка New tab, то сохраняем и текст из строки поиска
                new_data_state.append({'New tab': self.tab.widget(i).findChild(SearchClientStorage).search.text()})
            else:
                # Иначе сохраняем просто имя вкладки
                new_data_state.append(name_tab)
        SaveJsonFile('data/clients_manager/state_app', {'list_tab': new_data_state})

    def load_state_app(self):
        from widgets import ClientStorageWidget, SearchClientStorage
        from wallet import Wallet
        import requests
        from variables import DNS_NAME, PORT_DISPATCHER_CLIENTS_MANAGER

        last_state = LoadJsonFile('data/clients_manager/state_app').as_dict()  # Загружаем предыдущий state
        # И адреса client storages
        addresses_client = [Wallet(key).address for key in LoadJsonFile('data/clients_manager/key').as_list()]
        for name_tab in last_state['list_tab']:  # Восстанавливаем вкладки
            if type(name_tab) == dict:  # Если тип dict, то вкладка - New tab
                tabSearch = QFrame()
                search = SearchClientStorage()
                search.clientStoragesExplorer.change_path(name_tab['New tab'])  # Отображаем строку поиска из state
                search.changeSearchState.connect(self.save_state_app)
                search.openFogNodes.connect(self.open_tab_fog_nodes)
                search.createClientStorage.connect(self.create_client_storage)
                search.openClientStorages.connect(self.open_client_storages)
                search.openPool.connect(self.open_pool)
                tabSearch.setLayout(search)
                self.tab.addTab(tabSearch, 'New tab')

            elif name_tab == 'Pool':
                tabPool = QFrame()
                tabPool.setLayout(self.poolWidget)
                self.tab.addTab(tabPool, "Pool")

            elif name_tab == 'Fog Nodes':
                # Создание вкладки Fog node
                tabFogNodes = QFrame()
                self.fogNodesWidget.openPool.connect(self.open_pool)
                self.fogNodesWidget.changeBalanceClientsStorage.connect(self.change_balance_clients_storage)
                self.fogNodesWidget.changeBalancePool.connect(self.change_balance_pool)
                self.fogNodesWidget.createClientStorage.connect(self.create_and_open_client_storage)
                self.fogNodesWidget.openSettings.connect(self.open_settings)
                tabFogNodes.setLayout(self.fogNodesWidget)
                self.tab.addTab(tabFogNodes, "Fog Nodes")

            else:
                try:  # Адрес клиента
                    address = requests.get(
                        f'http://{DNS_NAME}:{PORT_DISPATCHER_CLIENTS_MANAGER}/api/address_normal/{name_tab}').json()
                except:
                    print(f'Клиента с именем {name_tab} не существует в сети')
                    continue
                if address in addresses_client:  # вкладка - client storage
                    tabClientStorages = QFrame()
                    clientStorageWidget = ClientStorageWidget(name_tab)
                    clientStorageWidget.changeNs.connect(self.change_ns_client_storage)
                    clientStorageWidget.openSettings.connect(self.open_settings)
                    # clientStorageWidget.change_balance(int(self.fogNodesWidget.fogNochange_address_client_storagedesTableWidget.item(
                    # self.fogNodesWidget.fogNodesTableWidget.currentRow(), 3).text()))
                    tabClientStorages.setLayout(clientStorageWidget)
                    self.tab.addTab(tabClientStorages, name_tab)

    def open_tab_fog_nodes(self):
        # Создание вкладки Fog node
        tabFogNodes = QFrame()
        self.fogNodesWidget.openPool.connect(self.open_pool)
        self.fogNodesWidget.changeBalanceClientsStorage.connect(self.change_balance_clients_storage)
        self.fogNodesWidget.changeBalancePool.connect(self.change_balance_pool)
        self.fogNodesWidget.createClientStorage.connect(self.create_and_open_client_storage)
        self.fogNodesWidget.openSettings.connect(self.open_settings)
        tabFogNodes.setLayout(self.fogNodesWidget)
        self.tab.insertTab(self.tab.count() -1 ,tabFogNodes, "Fog Nodes")
        self.tab.setCurrentIndex(self.tab.count() - 2)

    def new_window(self):
        from widgets import SearchClientStorage

        # Добавление новой вкладка поиска по storages
        tabSearch = QFrame()
        search = SearchClientStorage()
        search.changeSearchState.connect(self.save_state_app)
        search.openFogNodes.connect(self.open_tab_fog_nodes)
        search.createClientStorage.connect(self.create_client_storage)
        search.openClientStorages.connect(self.open_client_storages)
        search.openPool.connect(self.open_pool)
        tabSearch.setLayout(search)

        self.tab.insertTab(self.tab.count() - 1, tabSearch, 'New tab')
        self.tab.setCurrentIndex(self.tab.count() - 2)  # Открытие вкладки

    # -------------- Обработчики сигналов ClientStorageWidget --------------
    def change_ns_client_storage(self, ns, normal_address):
        from PyQt5.QtGui import QColor
        from PyQt5.QtWidgets import QTableWidgetItem
        from variables import POOL_BACKGROUND_COLOR, BACKGROUND_COLOR
        from widgets import ClientStorageWidget
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
        self.tab.setTabText(self.tab.currentIndex(), ns)  # Текущая вкладка - вкладка storage, имя которого изменяем
        # Изменяем адрес в explorer, для отображения короткого пути к объектам storage's

        # ------ Пример: -------
        # Путь к объекту storagre's через адрес  <адрес>/<id объекта>:
        # 521Fceb7C3b8E30aa200ACa5D6672A2b79Ad04b9/131061ca59a8adb856713e7f4de6b421efd1ca9ef96eac2a5f8d66e339084405
        # Путь к объекту storagre's через ns <ns>/<id объекта>:
        # PetrIvanov/131061ca59a8adb856713e7f4de6b421efd1ca9ef96eac2a5f8d66e339084405

        self.tab.widget(self.tab.currentIndex()).findChild(
            ClientStorageWidget).clientStoragesExplorer.change_name(ns)

    def create_client_storage(self):
        from wallet import Wallet
        wallet = Wallet()
        wallet.save_private_key('data/clients_manager/key')
        self.create_and_open_client_storage(wallet.address)

    def open_client_storages(self):
        from widgets import AllClientStorages

        all_client_storages = AllClientStorages()
        all_client_storages.selectedClientStorage.connect(self.create_and_open_client_storage)


    # -------------- Обработчики сигналов FogNodesWidget --------------
    def open_pool(self, private_key):
        from wallet import Wallet

        if not self.poolWidget.is_run():  # Если пул не запущен, но отпраляем запрос на запуск
            self.poolWidget.start_pool(private_key)
            self._address_pool = Wallet(private_key).address  # И сохраняем адресс

        index = self._get_index_name_tab('Pool')
        if index > -1:  # Если индекс != -1, то вкладка Pool существует
            self.tab.setCurrentIndex(index)  # Переходим на существующую вкладку
        else:
            # Иначе создаем вкладку Pool
            tabPool = QFrame()
            tabPool.setLayout(self.poolWidget)

            self.tab.insertTab(self.tab.count() - 1, tabPool, "Pool")
            self.tab.setCurrentIndex(self.tab.count() - 2)  # Открываем вкладку
            self.save_state_app()  # Сохраняем новое состояние приложения

    def change_balance_clients_storage(self, name, amount):
        from widgets import ClientStorageWidget

        # Изменение полного баланса storage
        for i in range(self.tab.count()):
            if self.tab.tabText(i) == name:  # Если имя вкладки совпадает с name,
                # отправляем запрос на изменение текщего баланса
                self.tab.widget(i).findChild(ClientStorageWidget).change_balance(amount)

    def change_balance_pool(self, amount):
        # Отправляем запрос на изменение pool баланса
        self.poolWidget.change_balance_pool(amount)

    def create_and_open_client_storage(self, address):
        from widgets import ClientStorageWidget

        index = self._get_index_name_tab(address)
        if index > -1:  # Если индекс != -1, то вкладка с названием address существует
            self.tab.setCurrentIndex(index)  # Переходим на существующую вкладку
        else:
            # Cоздаем вкладку
            tabClientStorages = QFrame()
            clientStorageWidget = ClientStorageWidget(address)
            clientStorageWidget.changeNs.connect(self.change_ns_client_storage)
            clientStorageWidget.openSettings.connect(self.open_settings)
            # Отображем полный баланс во вкладке
            clientStorageWidget.change_balance(int(self.fogNodesWidget.fogNodesTableWidget.item(
                self.fogNodesWidget.fogNodesTableWidget.currentRow(), 3).text()))
            tabClientStorages.setLayout(clientStorageWidget)

            self.tab.insertTab(self.tab.count() - 1, tabClientStorages, address)
            self.tab.setCurrentIndex(self.tab.count() - 2)  # Открываем вкладку
            self.save_state_app()  # Сохраняем новое состояние приложения

    # -------------- Общие обработчики сигналов FogNodesWidget и  ClientStorageWidget --------------
    def open_settings(self):
        from PyQt5.QtWidgets import QPushButton
        # Вкладка настроек
        tabSettings = QFrame()
        poolButton = QPushButton()  # Создать вкладку пула (если пул был активирован ранее)
        fogNodeButton = QPushButton()  # Создать вкладку со своими Fog nodes

        self.tab.insertTab(self.tab.count() - 1, tabSettings, 'Settings')
        self.tab.setCurrentIndex(self.tab.count() - 2)  # Открытие вкладки
