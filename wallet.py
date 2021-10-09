import hashlib
import os
from py_ecc import secp256k1


class Wallet:
    def __init__(self, private_key=None):
        self._private_key = private_key
        if self._private_key is None:
            self.generate_private_key()

    def generate_private_key(self):
        data = ''
        for i in range(100):
            data += str(os.urandom(64).hex())
        self._private_key = hashlib.sha3_256(bytes(data[:len(data)], 'utf-8')).hexdigest()

    def get_address(self):
        address = hashlib.sha3_256(bytes(self.get_public_key(), 'utf-8')).hexdigest()[-40:]
        return self.address_check_sum(address)

    def get_public_key(self):
        priv = int(self._private_key, 16).to_bytes(64, 'big')
        pub = secp256k1.privtopub(priv)
        pub = pub[0].to_bytes(32, 'big') + pub[1].to_bytes(32, 'big')
        pub = int.from_bytes(pub, 'big')
        return '0' * (128 - len(hex(pub)[2:])) + hex(pub)[2:]

    def address_check_sum(self, address):
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
        return address == self.address_check_sum(address)

    def save_private_key(self):
        path_file_key = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'key')
        if not os.path.exists(path_file_key):
            with open(path_file_key, 'w') as output:
                output.write('')

        with open(path_file_key, 'a') as output:
            output.write(self._private_key + "\n")
