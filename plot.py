import hashlib
import os
from wallet import Wallet
from dctp import ClientDCTP
import time
from threading import Thread

SIZE_BLOCK = 1024 ** 2
COUNT_BLOCKS_IN_PLOT = 100  # 30 * 1024
SLICE_FOR_RANDOM_HASH = 10


class Plot:
    def __init__(self, ip_addr_pool, port=5000, private_key=None):
        self._length_bin_data = None
        self._binary_data = None
        self._ip_addr_pool = ip_addr_pool
        self._port = port
        self._all_hash_blocks = {}
        self._client = ClientDCTP(private_key)
        self._client.connect(self._ip_addr_pool, self._port)
        if private_key is None:
            # Если не передаем в Plot private_key, то создаем его сами и получаем адрес
            # И инициализируем плот
            wallet = Wallet()
            wallet.save_private_key()
            self._id_plot = wallet.address

            # Создаем папку Plot, в которой будут храниться блоки
            os.mkdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'plots', self._id_plot))
            self._create_init_blocks()
        else:
            # Если передаем в Plot private_key, то получаем его адрес
            # И получаем его данные и проверяем их целостность
            wallet = Wallet(private_key)
            self._id_plot = wallet.address
            self._load_and_check_blocks()

    def _load_and_check_blocks(self):
        # Загружаем все данные в Plot, проверяем их целостность.
        path_plot = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'plots', self._id_plot)
        if os.path.exists(path_plot):
            for directory_path, directory_names, file_names in os.walk(path_plot):
                for file_name in file_names:
                    # Ноходим путь к файлу и сравниваем его с хэшом файла,
                    # проверяем в блокчейне существование данного хэша,
                    # в противном случаем удалем файл
                    hash_block = ''.join(directory_path[len(path_plot) + 1:].split('\\')) + file_name
                    file = open(os.path.join(directory_path, file_name), 'rb').read()
                    response = self._client.request('is_exist_block', data={'name': None, 'hash_list': hash_block})
                    if hashlib.sha3_256(file).hexdigest()[-len(hash_block):] == hash_block and \
                            (len(hash_block) == SLICE_FOR_RANDOM_HASH or (len(hash_block) == 64 and
                                                                          response['status'] == 0)):
                        self._all_hash_blocks[hash_block] = len(file)
                    else:
                        self._delete_block(hash_block)
            # Добавляем рандомные блоки, если какие-то файлы были удалены,
            # чтобы размер плота был = COUNT_BLOCKS_IN_PLOT * SIZE_BLOCK
            size = self.get_size_plot()
            while COUNT_BLOCKS_IN_PLOT * SIZE_BLOCK - size >= SIZE_BLOCK:
                self._create_init_block()
                size += SIZE_BLOCK

            return {"success": "Ok."}
        else:
            return {'error': f'Directory {self._id_plot} does not exist.'}

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

        return {"data": self._binary_data[SIZE_BLOCK * (part - 1): SIZE_BLOCK * part]}

    def _get_count_blocks_binary_data(self):
        # Возвращает количество блоков данных, на которые мы разбиваем self._binary_data по SIZE_BLOCK
        return int(self._length_bin_data / SIZE_BLOCK) + (self._length_bin_data % SIZE_BLOCK > 0)

    def load_data_from_blocks(self, list_hash_blocks):
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
        return {"success": "Ok."}

    def _create_init_blocks(self):
        # Создает COUNT_BLOCKS_IN_PLOT блоков со случайными данными
        # Это необходимо для того, чтобы заполнить Plot до максимального размера
        # т.к забиваем случайными данными, то хэши блоков будут разными.
        for block in range(COUNT_BLOCKS_IN_PLOT):
            result = self._create_init_block()
            if 'error' in result.keys():
                return result
        return {"success": "Ok."}

    def _create_init_block(self):
        # Создаем 1 блок со случайными данными.
        self.set_data(os.urandom(SIZE_BLOCK))
        result_save = self._save_data('')
        if 'error' in result_save.keys():
            return result_save
        return {"success": "Ok."}

    def get_id_plot(self):
        return self._id_plot

    def _save_data(self, name):
        # Сохраняет данные из self._binary_data в блоки

        # Разбивает self._binary_data на блоки размером по SIZE_BLOCK байт
        # И сохраняет их в отдельных файлах.
        # Путь (дерево из папок с названиями по 2 байта хэша, кроме последних 2) +
        # имя файла (последние 2 байта) = хэш блока

        # Пример:
        # 43be8Bf4B1C...73E60afc556Dр3 - хэш
        #  43\be\8B\f4\B1\...E6\0a\fc\55\6D\ - Путь из папок
        #  р3 - имя файла с данными блока
        hex_hash_list = []
        for count in range(self._get_count_blocks_binary_data()):
            block = self._get_part_binary_data(count + 1)
            if 'error' in block.keys():
                # если ошибка, то возвращаем ошибку
                return block

            hex_hash = hashlib.sha3_256(block['data']).hexdigest()

            if name == "":
                # если блок со случайными данными нужными только для того чтобы забить пустое пространство,
                # то хэш блока сокращаем до 10 символов. Это нужно для того, чтобы отличить их от нужных данных
                hex_hash = hex_hash[-SLICE_FOR_RANDOM_HASH:]

            # находим путь для сохранения разбивая хэш на пары. Создаемм папки и сохраняем файл
            path_hash_block = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'plots', self._id_plot,
                                           *[hex_hash[i:i + 2] for i in
                                             range(0, len(hex_hash) - 2, 2)])
            if not os.path.exists(path_hash_block):
                os.makedirs(path_hash_block)
            if not os.path.isfile(os.path.join(path_hash_block, hex_hash[-2:])):
                with open(os.path.join(path_hash_block, hex_hash[-2:]), 'wb') as output:
                    output.write(block['data'])
            else:
                pass
                # доработать в будущем проверку, если хэш файла одинаковым, а содержимое файлов разное

            # Добавляет в список self._all_hash_blocks хэши блоков
            self._all_hash_blocks[hex_hash] = len(block['data'])
            if name != "":
                hex_hash_list.append(hex_hash)

        # регестрируем транзакцию в блокчейне
        if name != "":
            response = self._client.request('new_transaction', data={'name': name, 'hash_list': hex_hash_list})
            if response['status'] != 0:
                print(response['status text'])
                # Доработать коды ошибок

        return {"success": "Ok."}

    def save_data(self, name):
        # Название файла не может быть = пустому значению,
        # т.к. пустые значения используются для названия начальных блоков с рандомыми значаниями
        if name == '':
            return {"error": "Parameter name must not be empty."}
        result = self._save_data(name)

        size = self.get_size_plot() - COUNT_BLOCKS_IN_PLOT * SIZE_BLOCK
        # Флаг для отслеживания, был ли удален хотя бы 1 блок со случайными данными
        random_block_is_del = False

        # Удаляем блоки со случайными данными из Plot, если размер Plot > COUNT_BLOCKS_IN_PLOT * SIZE_BLOCK
        if size > 0:
            for key in list(self._all_hash_blocks.keys()).copy():
                if len(key) == SLICE_FOR_RANDOM_HASH:
                    random_block_is_del = True
                    size -= SIZE_BLOCK

                    # Удаляем данные о блоке
                    self._all_hash_blocks.pop(key)
                    self._delete_block(key)

                    if size < 0:
                        # Доработать выход из цикла
                        break
            if not random_block_is_del:
                pass
                # Доработать при готовности ноды на удаление файлов, с большей репликацией

        return result

    def _delete_block(self, id_block):
        # Удаляем файл  и пустые папки с названием id_block

        path_to_file = [id_block[i:i + 2] for i in range(0, len(id_block) - 2, 2)]
        # Удаляем файл с бинарными данными
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'plots', self._id_plot,
                               *path_to_file, id_block[-2:]))
        try:
            # Удаляет пустые папки по пути к файлу
            for i in range(len(path_to_file), 0, -1):
                os.rmdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'plots',
                                      self._id_plot, *path_to_file[:i]))
        except:
            # Если папка не пустая, то срабатывает исключение и папка не удаляется
            pass

    def get_all_hash_blocks(self):
        # Возвращает хэши всех блоков в данном плоте
        return self._all_hash_blocks

    def get_size_plot(self):
        # Возвращает размер всех данных в плоте
        return sum([self._all_hash_blocks[key] for key in self._all_hash_blocks.keys()])

    def start(self):
        def worker():
            while True:
                time.sleep(10)

        # run node
        job_node = Thread(target=worker)
        job_node.start()

        print(f'Plot {self._id_plot} готов к работе')
