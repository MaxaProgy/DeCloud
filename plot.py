import hashlib
import os
from wallet import Wallet
from blockchain import blockchain



SIZE_BLOCK = 1024 ** 2
COUNT_BLOCKS_IN_PLOT = 100  # 30 * 1024


class Plot:
    def __init__(self, id_plot=None):
        self._length_bin_data = None
        self._binary_data = None
        self._all_hash_blocks = []

        # Устанавливаем address как индификатор плота
        # self._id_plot - это адрес Wallet, к которому привязан данные плот
        # Если id_plot не указан, то создаем новый Wallet и сами указываем адрес

        self._id_plot = id_plot
        if self._id_plot is None:
            wallet = Wallet()
            wallet.save_private_key()
            self._id_plot = wallet.get_address()

        # Создаем папку Plot, в которой будут храниться блоки
        os.mkdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'plots', self._id_plot))
        self._create_init_blocks()

    def load_from_file(self, file_name):
        # Загрузка данных из файла
        self.set_data(open(file_name, "rb").read())

    def save_to_file(self, file_name):
        # Запись в файл
        with open(file_name, 'wb') as output:
            output.write(self._binary_data)

    def set_data(self, binary_data):
        # Сохраняет данные в self._binary_data
        self._binary_data = binary_data
        self._length_bin_data = len(self._binary_data)

    def _get_part_binary_data(self, part):
        # В зависимости от SIZE_BLOCK возвращает срез part - части данных

        if self._binary_data is None:
            return {"error": "File not load. Use method load_file"}
        if self._get_count_blocks_binary_data() < part:
            return {"error": f"File have not block number {part}."}
        if part < 1:
            return {"error": "Param size_part must be greater than zero."}

        return self._binary_data[SIZE_BLOCK * (part - 1): SIZE_BLOCK * part]

    def _get_count_blocks_binary_data(self):
        # Возвращает количество блоков данных, на которые мы разбиваем self._binary_data по SIZE_BLOCK
        return int(self._length_bin_data / SIZE_BLOCK) + (self._length_bin_data % SIZE_BLOCK > 0)

    def _load_data_from_blocks(self, list_hash_blocks):
        # По списку хэшей находит блоки, объединяет данные из блоков и конечные данные записывает в self._binary_data

        binary_data = b""
        for hash_block in list_hash_blocks:
            path_hash_block = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'plots', self._id_plot,
                                           *[hash_block[i:i + 2] for i in range(0, len(hash_block), 2)])
            if os.path.isfile(path_hash_block):
                binary_data += open(path_hash_block, 'rb').read()
            else:
                return {"error": f"File {hash_block} not found."}
        self.set_data(binary_data)

    def _save_data_to_blocks(self):
        # Разбивает self._binary_data на блоки размером по SIZE_BLOCK байт
        # И сохраняет их в отдельных файлах.
        # Путь (дерево из папок с названиями по 2 байта хэша, кроме последних 2) +
        # имя файла (последние 2 байта) = хэш блока

        # Пример:
        # 43be8Bf4B1C...73E60afc556Dр3 - хэш
        #  43\be\8B\f4\B1\...E6\0a\fc\55\6D\ - Путь из папок
        #  р3 - имя файла с данными блока

        for count in range(self._get_count_blocks_binary_data()):
            value = self._get_part_binary_data(count + 1)
            hex_hash = hashlib.sha3_256(value).hexdigest()
            path_hash_block = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'plots', self._id_plot,
                                           *[hex_hash[i:i + 2] for i in
                                             range(0, len(hex_hash) - 2, 2)])
            if not os.path.exists(path_hash_block):
                os.makedirs(path_hash_block)
            if not os.path.isfile(os.path.join(path_hash_block, hex_hash[-2:])):
                with open(os.path.join(path_hash_block, hex_hash[-2:]), 'wb') as output:
                    output.write(value)
            else:
                pass
                # доработать в будущем, если содержимое файлов разное

    def _create_init_blocks(self):
        # Создает COUNT_BLOCKS_IN_PLOT блоков со случайными данными
        # Это необходимо для того, чтобы заполнить Plot до максимального размера
        # т.к забиваем случайными данными, то хэши блоков будут разными.
        for block in range(COUNT_BLOCKS_IN_PLOT):
            self.set_data(os.urandom(SIZE_BLOCK))
            self.save_data('')

    def get_id_plot(self):
        return self._id_plot

    def save_data(self, name):
        # Сохраняет данные из self._binary_data в блоки
        self._save_data_to_blocks()
        # Добавляет в список self._all_hash_blocks хэши блоков
        for count in range(self._get_count_blocks_binary_data()):
            hash_block = hashlib.sha3_256(self._get_part_binary_data(count + 1)).hexdigest()
            self._all_hash_blocks.append(hash_block)
            blockchain.transaction[name] = blockchain.transaction.get(name, []) + [hash_block]

    def get_all_hash_blocks(self):
        # Возвращает хэши всех блоков в данном плоте
        return self._all_hash_blocks



