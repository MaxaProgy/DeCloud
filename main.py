import hashlib
import os

MB = 1024 ** 2


class FileBlock:
    def __init__(self, file_name, size_block):
        self._bin_file = None
        self._size_block = None
        self._length_bin_file = None
        self._dictionary_file_hash_value = dict()

        self.load_file(file_name)
        self.set_size_block(size_block)

    def set_size_block(self, size_block):
        if size_block < 1:
            return {"error": "Param size_part must be greater than zero."}
        self._size_block = size_block

    def load_file(self, path_file):
        self._bin_file = open(path_file, "rb").read()
        self._length_bin_file = len(self._bin_file)

    def get_part_file(self, k):
        if self._size_block is None:
            return {"error": "Not size part. Use method set_size_block"}
        if self._bin_file is None:
            return {"error": "File not load. Use method load_file"}
        if self.get_count_block() < k:
            return {"error": f"File have not block number {k}."}
        if k < 1:
            return {"error": "Param size_part must be greater than zero."}

        return self._bin_file[self._size_block * (k - 1): self._size_block * k]

    def get_count_block(self):
        return int(self._length_bin_file / self._size_block) + (self._length_bin_file % self._size_block > 0)

    def save_blocks(self):
        for k in range(file_block.get_count_block()):
            value = file_block.get_part_file(k + 1)
            hex_hash = hashlib.sha3_256(value).hexdigest()
            os.chdir(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')))
            for i in range(0, len(hex_hash) - 2, 2):
                name = hex_hash[i: i + 2]
                if not name in os.listdir(path="."):
                    os.mkdir(os.path.abspath(name))
                os.chdir(os.path.abspath(name))
            with open(hex_hash[-2:], 'wb') as output:
                output.write(value)


if __name__ == '__main__':
    file_block = FileBlock(input("Введите путь к файлу: "), MB)
