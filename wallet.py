from _pysha3 import keccak_256 as sha3_256
import json
import os
from py_ecc.secp256k1 import ecdsa_raw_sign, ecdsa_raw_recover, privtopub

from utils import LoadJsonFile, SaveJsonFile


class Wallet:
    def __init__(self, private_key=None):
        self._private_key = private_key
        if self._private_key is None:
            # Если не передаем private_key в Wallet, то сохдаем его сами
            self.generate_private_key()

    def generate_private_key(self):
        # Создание private_key
        # Формируем случайный набор данных и находим от него хэш = private_key
        self._private_key = sha3_256(bytes(''.join([os.urandom(64).hex() for _ in range(100)]), 'utf-8')).hexdigest()

    @staticmethod
    def address_build_checksum(address):
        # Формируем address по следующему условию:
        # Если каждый 4 символ в address буква от a до f, то меняем их регистр с lower на upper
        address = address.lower()
        hash_addr = bin(int(sha3_256(address.encode()).hexdigest(), 16))
        hash_addr = '0' * (256 - len(hash_addr)) + hash_addr[2:]
        res = ''
        for i in range(len(address)):
            if address[i].isalpha() and hash_addr[4 * i] == '1':
                res += address[i].upper()
            else:
                res += address[i]
        return res

    @staticmethod
    def check_valid_address(address):
        # Проверяем правильность ввода address
        return address == Wallet.address_build_checksum(address)

    @staticmethod
    def sign_verification(data, sign, public_key):
        """
        Recovers the owner's public key using the document and its signature
        :param    data: data transaction
        :param    sign: signatura data transaction
        :return       : public key owner this document
        """

        sign = (int(sign[0:4], 16), int(sign[4:68], 16), int(sign[68:], 16),)
        data = sha3_256(bytes(json.dumps(data), 'utf-8')).digest()
        pub = ecdsa_raw_recover(data, sign)
        pub = pub[0].to_bytes(32, 'big') + pub[1].to_bytes(32, 'big')
        pub = int.from_bytes(pub, 'big')
        pub = ('0' * (128 - len(hex(pub)[2:])) + hex(pub)[2:])
        return pub == public_key



    def _pub_to_address(self, public_key):
        return self.address_build_checksum(sha3_256(bytes(public_key, 'utf-8')).hexdigest()[-40:])

    @property
    def address(self):
        return self._pub_to_address(self.public_key)

    @property
    def private_key(self):
        return self.private_key

    @property
    def public_key(self):
        # Создаем public_key через private_key
        private_key = int(self._private_key, 16).to_bytes(32, 'big')
        public_key = privtopub(private_key)
        public_key = public_key[0].to_bytes(32, 'big') + public_key[1].to_bytes(32, 'big')
        public_key = int.from_bytes(public_key, 'big')

        # Делаем так, чтобы ключь всегда был одной длины
        return '0' * (128 - len(hex(public_key)[2:])) + hex(public_key)[2:]

    def save_private_key(self, path):
        # Сохраняем private_key в файл
        SaveJsonFile(path=path, data=LoadJsonFile(path=path).as_list()+[self._private_key])

    def sign(self, data):
        """
            Signing a document at the wallet address with a private key
        :param    data: data transaction
               address: address wallet
        :return       : signatura
        """

        data = sha3_256(bytes(json.dumps(data), 'utf-8')).digest()
        ans = ecdsa_raw_sign(data, int(self._private_key, 16).to_bytes(64, 'big'))
        res = '0x'
        for j in range(3):
            if j > 0:
                res += '0' * (64 - len(hex(ans[j])[2:])) + hex(ans[j])[2:]
            else:
                res += '0' * (2 - len(hex(ans[j])[2:])) + hex(ans[j])[2:]
        return res
