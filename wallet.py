import hashlib
import os
from py_ecc import secp256k1


class Wallet:
    def __init__(self, private_key=None):
        self._private_key = private_key
        if self._private_key is None:
            # Если не передаем private_key в Wallet, то сохдаем его сами
            self.generate_private_key()

    def generate_private_key(self):
        # Создание private_key
        # Формируем случайный набор данных и находим от него хэш = private_key
        data = ''
        for i in range(100):
            data += str(os.urandom(64).hex())
        self._private_key = hashlib.sha3_256(bytes(data, 'utf-8')).hexdigest()

    @property
    def address(self):
        address = hashlib.sha3_256(bytes(self.get_public_key(), 'utf-8')).hexdigest()[-40:]
        return self._address_check_sum(address)

    def get_public_key(self):
        # Создаем public_key через private_key
        private_key = int(self._private_key, 16).to_bytes(64, 'big')
        public_key = secp256k1.privtopub(private_key)
        public_key = public_key[0].to_bytes(32, 'big') + public_key[1].to_bytes(32, 'big')
        public_key = int.from_bytes(public_key, 'big')
        # Делаем так, чтобы ключь всегда был одной длины
        return '0' * (128 - len(hex(public_key)[2:])) + hex(public_key)[2:]

    @staticmethod
    def _address_check_sum(address):
        # Формируем address по следующему условию:
        # Если каждый 4 символ в address буква от a до f, то меняем их регистр с lower на upper
        address = address.lower()
        hash_addr = bin(int(hashlib.sha3_256(address.encode()).hexdigest(), 16))
        hash_addr = '0' * (256 - len(hash_addr)) + hash_addr[2:]
        res = ''
        for i in range(len(address)):
            if address[i].isalpha() and hash_addr[4 * i] == '1':
                res += address[i].upper()
            else:
                res += address[i]
        return res

    def check_valid_address(self, address):
        # Проверяем правильность ввода address
        return address == self._address_check_sum(address)

    def save_private_key(self):
        # Сохраняем private_key в файл
        path_file_key = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'storages', 'key')
        if not os.path.exists(path_file_key):
            with open(path_file_key, 'w') as output:
                output.write('')

        with open(path_file_key, 'a') as output:
            output.write(self._private_key + "\n")
