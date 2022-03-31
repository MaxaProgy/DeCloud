from utils import LoadJsonFile
from wallet import Wallet


class DNS:
    def __init__(self, dispatcher_save):
        self._ns_table = LoadJsonFile('data/pool/dns').as_dict()
        self._dispatcher_save = dispatcher_save

    def add_ns(self, name, address):
        self._ns_table[name] = address

        self._dispatcher_save.add('data/pool/dns', self._ns_table)
        print('Add NS record', name, address)

    def find_address(self, name):
        if Wallet.check_valid_address(name):
            return name
        elif name in self._ns_table:
            return self._ns_table[name]

    def get_all_ns(self, address):
        return {address: [key for key, item in self._ns_table.items() if item == address]}
