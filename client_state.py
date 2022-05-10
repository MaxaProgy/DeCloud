import datetime

from utils import exists_path, LoadJsonFile, SaveJsonFile
from wallet import Wallet


class ClientState:
    # Класс состояния клиента, его файлов
    def __init__(self, parent, address):
        self._address = address
        address_normal = parent._dns.find_address(address)
        if address_normal:
            self._address = address_normal

        self._server_fn = parent._server_fn
        self._state_client = {'all_balance': 0, 'occupied_balance': 0, 'objects': {}}
        self._path = f'data/pool/state/{"/".join([self._address[i:i + 2] for i in range(0, len(self._address), 2)])}'
        self._load_state()

    def _load_state(self):
        # Загрузка предыдущего состояния из файла
        if not exists_path(self._path):
            return
        self._state_client = LoadJsonFile(self._path).as_dict()

    def _save_state(self):
        # Загрузка текущего состояния в файл
        SaveJsonFile(path=self._path, data=self._state_client)

    def add_object(self, id_object, size):
        # Добавление нового объекта клиента
        self._state_client['objects'][id_object] = {'date': datetime.datetime.utcnow().timestamp(),
                                                    'size': size}
        self._save_state()

    def info_object(self, id_object):
        # Возвращение информации объекта (файл, директория), его время создания и размер
        if id_object in self._state_client['objects'].keys():
            return self._state_client['objects'][id_object]
        return {}

    @property
    def all_balance(self):
        return self._state_client['all_balance']

    @all_balance.setter
    def all_balance(self, amount):
        self._state_client['all_balance'] = amount
        self._save_state()
        if self._address in self._server_fn.get_workers():
            try:
                self._server_fn.request(id_worker=self._address, method='update_balance',
                                        json={'amount': self._state_client['all_balance']})
            except:
                pass

    @property
    def occupied_balance(self):
        return self._state_client['occupied_balance']

    @occupied_balance.setter
    def occupied_balance(self, amount):
        self._state_client['occupied_balance'] = amount
        self._save_state()
