import time

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QTabWidget, QFrame, QMenu, QAction, QTabBar, QToolButton, \
    QLabel, QTableWidgetItem

from variables import POOL_BACKGROUND_COLOR, BACKGROUND_COLOR
from widgets import FogNodesWidget, PoolWidget, ClientStorageWidget, SearchClientStorage
from utils import exists_path, LoadJsonFile, SaveJsonFile
from wallet import Wallet


class AppClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self._address_pool = LoadJsonFile('data/pool/key').as_string()

        self.initUI()

    def initUI(self):
        self.geometry = QDesktopWidget().availableGeometry()
        self.setGeometry(1000, 1000, 1000, 800)
        self.move(500, 100)
        self.fogNodesWidget = FogNodesWidget()
        self.poolWidget = PoolWidget()
        self.tab = QTabWidget()
        self.tab.setTabsClosable(True)
        self.tab.setMovable(True)
        self.tab.tabCloseRequested.connect(self.closeTab)

        if exists_path('data/clients_manager/state_app'):
            self.load_state_app()
        else:
            tabFogNodes = QFrame()
            self.fogNodesWidget.createPool.connect(self.start_pool)
            self.fogNodesWidget.changeBalanceClientsStorage.connect(self.change_balance_clients_storage)
            self.fogNodesWidget.changeBalancePool.connect(self.change_balance_pool)
            self.fogNodesWidget.createClientStorage.connect(self.create_and_open_client_storage)
            tabFogNodes.setLayout(self.fogNodesWidget)
            self.tab.addTab(tabFogNodes, "Fog Nodes")
        self.tab.addTab(QLabel(""), '')
        self.addTabButton = QToolButton()
        self.addTabButton.setText('+')
        self.addTabButton.clicked.connect(self.new_window)
        self.tab.tabBar().setTabButton(self.tab.count() - 1, QTabBar.RightSide, self.addTabButton)
        self.tab.setTabEnabled(self.tab.count() - 1, False)

        self.setCentralWidget(self.tab)

        self.setWindowTitle("DeCloud")

    def new_window(self):
        tabSearch = QFrame()
        search = SearchClientStorage()
        search.change_search_state.connect(self.save_state_app)
        tabSearch.setLayout(search)

        self.tab.insertTab(self.tab.count() - 1, tabSearch, 'New tab')
        self.tab.setCurrentIndex(self.tab.count() - 2)

    def change_balance_pool(self, amount):
        self.poolWidget.change_balance_pool(amount)

    def change_balance_clients_storage(self, address, amount):
        for i in range(self.tab.count()):
            if self.tab.tabText(i) == address:
                self.tab.widget(i).findChild(ClientStorageWidget).change_balance(amount)

    def closeTab(self, ind):  # метод закрывает вкладку под номером ind
        self.tab.removeTab(ind)

    def start_pool(self, private_key):
        if not self.poolWidget.is_run():
            self.poolWidget.start_pool(private_key)
            self._address_pool = Wallet(private_key).address

        index = self._get_index_name_tab('Pool')
        if index > -1:
            self.tab.setCurrentIndex(index)
        else:
            tabPool = QFrame()
            tabPool.setLayout(self.poolWidget)
            self.tab.insertTab(self.tab.count() - 1, tabPool, "Pool")
            self.tab.setCurrentIndex(self.tab.count() - 2)
            self.save_state_app()

    def closeEvent(self, event):
        self.showMinimized()
        event.ignore()

    def save_state_app(self):
        new_data_state = []
        for i in range(self.tab.count()):
            name_tab = self.tab.tabText(i)
            if name_tab == 'New tab':
                new_data_state.append({'New tab': self.tab.widget(i).findChild(SearchClientStorage).search.text()})
            else:
                new_data_state.append(name_tab)
        SaveJsonFile('data/clients_manager/state_app', {'list_tab': new_data_state})

    def load_state_app(self):
        last_state = LoadJsonFile('data/clients_manager/state_app').as_dict()
        addresses_client = [Wallet(key).address for key in LoadJsonFile('data/clients_manager/key').as_list()]
        for address in last_state['list_tab']:
            if type(address) == dict:
                tabSearch = QFrame()
                search = SearchClientStorage()
                search.clientStoragesExplorer.change_path(address['New tab'])
                search.change_search_state.connect(self.save_state_app)
                tabSearch.setLayout(search)
                self.tab.addTab(tabSearch, 'New tab')

            elif address == 'Pool':
                tabPool = QFrame()
                tabPool.setLayout(self.poolWidget)
                self.tab.addTab(tabPool, "Pool")

            elif address == 'Fog Nodes':
                tabFogNodes = QFrame()
                self.fogNodesWidget.createPool.connect(self.start_pool)
                self.fogNodesWidget.changeBalanceClientsStorage.connect(self.change_balance_clients_storage)
                self.fogNodesWidget.changeBalancePool.connect(self.change_balance_pool)
                self.fogNodesWidget.createClientStorage.connect(self.create_and_open_client_storage)
                tabFogNodes.setLayout(self.fogNodesWidget)
                self.tab.addTab(tabFogNodes, "Fog Nodes")

            elif address in addresses_client:
                tabClientStorages = QFrame()
                clientStorageWidget = ClientStorageWidget(address)
                clientStorageWidget.change_ns.connect(self.change_ns_client_storage)
                #clientStorageWidget.change_balance(int(self.fogNodesWidget.fogNochange_address_client_storagedesTableWidget.item(
                   # self.fogNodesWidget.fogNodesTableWidget.currentRow(), 3).text()))
                tabClientStorages.setLayout(clientStorageWidget)
                self.tab.addTab(tabClientStorages, address)

    def _get_index_name_tab(self, address):
        for i in range(self.tab.count()):
            if address == self.tab.tabText(i):
                return i
        return -1

    def create_and_open_client_storage(self, address):
        index = self._get_index_name_tab(address)
        if index >= 0:
            self.tab.setCurrentIndex(index)
        else:
            for key in LoadJsonFile('data/fog_nodes/key').as_list():
                wallet = Wallet(key)
                if wallet.address == address:
                    if key not in LoadJsonFile('data/clients_manager/key').as_list():
                        Wallet(key).save_private_key('data/clients_manager/key')
                    break

            tabClientStorages = QFrame()
            clientStorageWidget = ClientStorageWidget(address)
            clientStorageWidget.change_ns.connect(self.change_ns_client_storage)
            clientStorageWidget.change_balance(int(self.fogNodesWidget.fogNodesTableWidget.item(
                self.fogNodesWidget.fogNodesTableWidget.currentRow(), 3).text()))
            tabClientStorages.setLayout(clientStorageWidget)
            self.tab.insertTab(self.tab.count() - 1, tabClientStorages, address)
            self.tab.setCurrentIndex(self.tab.count() - 2)
            self.save_state_app()

    def change_ns_client_storage(self, ns, address):
        for i in range(self.fogNodesWidget.fogNodesTableWidget.rowCount()):
            if self.fogNodesWidget.fogNodesTableWidget.item(i, 4).text() == address:
                color_background = self.fogNodesWidget.fogNodesTableWidget.item(i, 0).background().color().name()
                if color_background != POOL_BACKGROUND_COLOR:
                    color_background = BACKGROUND_COLOR
                color_foreground = self.fogNodesWidget.fogNodesTableWidget.item(i, 0).foreground().color()
                self.fogNodesWidget.fogNodesTableWidget.setSortingEnabled(False)
                self.fogNodesWidget.fogNodesTableWidget.setItem(i, 0, QTableWidgetItem(ns))
                self.fogNodesWidget.fogNodesTableWidget.item(i, 0).setBackground(QColor(color_background))
                self.fogNodesWidget.fogNodesTableWidget.item(i, 0).setForeground(color_foreground)
                self.fogNodesWidget.fogNodesTableWidget.setSortingEnabled(True)
                break

        self.tab.setTabText(self.tab.currentIndex(), ns)
        self.tab.widget(self.tab.currentIndex()).findChild(ClientStorageWidget).clientStoragesExplorer.change_address(ns)
