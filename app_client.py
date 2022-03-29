from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QTabWidget, QFrame, QMenu, QAction, QTabBar, QToolButton, \
    QLabel
from widgets import FogNodesWidget, PoolWidget, ClientStorageWidget, SearchClientStorage
from utils import exists_path, LoadJsonFile, SaveJsonFile
from wallet import Wallet


class AppClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self._address_pool = ''
        #self.load_params()
        self.initUI()


    def initUI(self):
        self.geometry = QDesktopWidget().availableGeometry()
        self.setGeometry(1000, 1000, 1000, 800)
        self.move(500, 100)

        self.poolWidget = PoolWidget()

        tabFogNodes = QFrame()
        self.fogNodesWidget = FogNodesWidget()
        self.fogNodesWidget.createPool.connect(self.start_pool)
        self.fogNodesWidget.changeBalance.connect(self.change_balance)
        self.fogNodesWidget.createClientStorage.connect(self.create_and_open_client_storage)
        tabFogNodes.setLayout(self.fogNodesWidget)

        self.tab = QTabWidget()
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.closeTab)

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
        tabSearch.setLayout(search)

        self.tab.insertTab(self.tab.count() - 1, tabSearch, 'New tab')
        self.tab.setCurrentIndex(self.tab.count() - 2)



    def change_balance(self, address, amount):
        if address == self._address_pool:
            self.poolWidget.change_balance_pool(amount)

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

    def closeEvent(self, event):
        self.showMinimized()
        event.ignore()

    def save_params(self):
        pass

    def load_params(self):
        pass

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
            clientStorageWidget.change_balance(int(self.fogNodesWidget.fogNodesTableWidget.item(
                self.fogNodesWidget.fogNodesTableWidget.currentRow(), 3).text()))
            tabClientStorages.setLayout(clientStorageWidget)
            self.tab.insertTab(self.tab.count() - 1, tabClientStorages, address)
            self.tab.setCurrentIndex(self.tab.count() - 2)

    def create_client_storage_for_pool(self):
        key = LoadJsonFile('data/pool/key').as_list()[0]
        self.client_storages[self._address_pool] = {'wallet': Wallet(key), 'id_current_dir': None}
        self.client_storages[self._address_pool]['wallet'].save_private_key('data/clients_manager/key')
        self.setWindowTitle("DeCloud  —  " + self._address_pool)
        self.labelAmountClient.setText(self.labelAmountPool.text())
        self.current_client_storage_full_amount = self.pool_balance
        self.set_current_address_client_storage(self._address_pool)
        self.current_id_dir = None
        self.show_current_dir()
        self.tab.setCurrentIndex(0)
        self.sendDomainNameRegistrationAction.setEnabled(True)
        self._createMenuBar()

