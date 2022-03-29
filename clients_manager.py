# -*- coding: utf-8 -*
import random
from multiprocessing import Process
from queue import Queue
import json

import requests

from dctp import ClientDCTP
from fog_node import BaseFogNode, SIZE_REPLICA
from flask import Flask, request, jsonify, Response, abort
from utils import get_pools_host, LoadJsonFile, SaveJsonFile
from wallet import Wallet

SESSION_TIME_LIFE = 24 * 60 * 60


class FileExplorer:
    def __init__(self, name, hash):
        self._name = name
        self._hash = hash
        self._state = False

    @property
    def name(self):
        return self._name

    @property
    def hash(self):
        return self._hash

    def is_file(self):
        # Проверяем на файл ли это
        return type(self) == FileExplorer


class DirectoryExplorer:
    def __init__(self, name, hash, parent):
        self._name = name
        self._hash = hash
        self._children = []
        self._parent = parent
        self._state = False

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def hash(self):
        return self._hash

    def get_children(self):
        return self._children

    def add_child(self, child):
        # Добавление вложеных в директорию директорий и папок
        self._children.append(child)

    def is_file(self):
        # Проверяем на файл ли это
        return type(self) == FileExplorer


class ClientStorageExplorer(BaseFogNode):
    # Файловая система
    def __init__(self, address):
        BaseFogNode.__init__(self)

        self._id_fog_node = address
        # Создание корневной - главной директории
        self._main_dir_data = 'clients_manager'
        self._root_dir = DirectoryExplorer(self._id_fog_node, None, None)

        self._load_state()

    @property
    def root_dir(self):
        return self._root_dir

    def _load_state(self):
        hashes_explorer = LoadJsonFile(path=f'data/clients_manager/{self._id_fog_node}/state.json').as_list()
        for hash in hashes_explorer:  # Проходим по всем
            info_params_obj = json.loads(self._load_replica(hash))  # Формируем json из бинарных данных файла
            if info_params_obj[0] == 'file':  # Если файл
                file = FileExplorer(info_params_obj[2], hash)  # Создаем файл
                # Находим папку и добавляем к ней в качестве child - файл
                self.find_object_on_hash(info_params_obj[1]).add_child(file)
            elif info_params_obj[0] == 'dir':  # если папка
                parent = self.find_object_on_hash(info_params_obj[1])  # Находим папку
                # Добавляем к ней в качестве child - файл
                child = DirectoryExplorer(info_params_obj[2], hash, parent)
                parent.add_child(child)

    def save_state(self):
        from queue import Queue
        task_queue = Queue()
        task_queue.put(self.root_dir)  # Очаредь всех вершин графа
        hashes_explorer = [self.root_dir.hash]  # Список хэшей-путей к файлам
        while not task_queue.empty():
            current_obj = task_queue.get()  # Забираем объект
            if not current_obj.is_file():
                # Если файл, то добавляем всех его children в очаредь вершин графа и
                # сохраняем в спиок хэши-пути к файлам
                [task_queue.put(child) for child in current_obj.get_children()]
                hashes_explorer += [child.hash for child in current_obj.get_children()]
            # Сохраняем в файл все хэши к файлам
            SaveJsonFile(path=f'data/clients_manager/{self._id_fog_node}/state.json',
                         data=hashes_explorer[1:])  # первый в списке - текущая папка

    def find_object_on_hash(self, hash):
        # Находим папку по хэшу
        task_queue = Queue()
        task_queue.put(self.root_dir)
        while not task_queue.empty():
            current_obj = task_queue.get()
            if hash == current_obj.hash:
                # Если хэш совпадает с хешом текущего, то возращаем
                return current_obj
            if not current_obj.is_file():  # Если не файл
                [task_queue.put(child) for child in current_obj.get_children()]

        return None


class DispatcherClientsManager(Process):
    def __init__(self, port):
        Process.__init__(self)
        self._port = port
        self._session_keys = {}

    def run(self):
        pools = get_pools_host('data/pool/pools_host')
        ip, port, port_cm, _ = pools[random.choice(list(pools.keys()))]

        client_pool = ClientDCTP(f'CM-{Wallet().address}', ip, port_cm)
        client_pool.start()

        app = Flask(__name__)

        @app.route('/api/registration_domain_name', methods=['POST'])
        def registration_domain_name():
            data = request.json
            try:
                return jsonify(client_pool.request(id_client=data['address'],
                                                   method='registration_domain_name', json=data))
            except:
                abort(404)

        @app.route('/api/get_balance/<address>', methods=['GET'])
        def get_balance(address):
            try:
                return jsonify(requests.get(f'http://{ip}:{port}/get_balance/{address}').json())
            except:
                abort(404)

        @app.route('/api/get_free_balance/<address>', methods=['GET'])
        def get_free_balance(address):
            try:
                return jsonify(requests.get(f'http://{ip}:{port}/get_free_balance/{address}').json())
            except:
                abort(404)

        @app.route('/api/new_transaction', methods=['POST'])
        def new_transaction():
            data = request.json
            try:
                return jsonify(client_pool.request(id_client=data['sender'], method='new_transaction', json=data))
            except:
                abort(404)

        @app.route('/api/save_file', methods=['POST'])
        def save_file():
            # Добавляем файл в файловую сиситему
            data = dict(request.args)
            if not all([key in data.keys() for key in ['address', 'public_key', 'file_name', 'sign']]):
                return jsonify({'error': 'required parameters are not specified: public_key, file, sign'})
            sign = data.pop('sign')
            if not Wallet.sign_verification(data=data, sign=sign, public_key=data['public_key']):
                return jsonify({'error': 'signature is not valid'})

            client = ClientStorageExplorer(data['address'])
            current_dir = client.find_object_on_hash(None)
            if 'id_current_dir' in data.keys():
                current_dir = client.find_object_on_hash(data['id_current_dir'])

            if data['file_name'] in [child.name for child in current_dir.get_children() if child.is_file()]:
                return jsonify({'error': f'the current object already has the given name {data["file_name"]}'})

            hashes = []
            i = 0
            while True:
                i += 1
                chunk = request.stream.read(SIZE_REPLICA)
                if not chunk:
                    break
                hashes.append(client._save_replica(chunk))
                client_pool.request(id_client=data['address'], method='send_replica', data=chunk)
            chunk = bytes(json.dumps(['file', current_dir.hash, data['file_name'], hashes]), 'utf-8')
            hash_file = client._save_replica(chunk)

            client_pool.request(id_client=data['address'], method='send_replica', data=chunk)
            client_pool.request(id_client=data['address'], method='commit_replica', json={'data': hash_file})

            current_dir.add_child(FileExplorer(data['file_name'], hash_file))
            client.save_state()

            return jsonify()

        @app.route('/api/make_dir', methods=['GET'])
        def make_dir():
            data = request.json
            if not all([key in data.keys() for key in ['address', 'public_key', 'name', 'sign']]):
                return jsonify({'error': 'required parameters are not specified: public_key, name, sign'})

            sign = data.pop('sign')
            if not Wallet.sign_verification(data=data, sign=sign, public_key=data['public_key']):
                return jsonify({'error': 'signature is not valid'})

            if data['name'] == '..' or '/' in data['name']:
                return jsonify({'error': 'invalid characters in name'})

            client = ClientStorageExplorer(data['address'])
            current_dir = client.find_object_on_hash(None)
            if 'id_current_dir' in data.keys():
                current_dir = client.find_object_on_hash(data['id_current_dir'])

            name = data['name']
            if name in [child.name for child in current_dir.get_children() if not child.is_file()]:
                return jsonify({'error': f'the current object already has the given name {name}'})

            hash_dir = client._save_replica(bytes(json.dumps(['dir', current_dir.hash, name]), 'utf-8'))

            client_pool.request(id_client=data['address'], method='send_replica',
                                data=bytes(json.dumps(['dir', current_dir.hash, name]), 'utf-8'))
            client_pool.request(id_client=data['address'], method='commit_replica', json={'data': hash_dir})

            current_dir.add_child(DirectoryExplorer(name, hash_dir, current_dir))
            client.save_state()

            return jsonify(hash_dir)

        @app.route('/api/get_object', methods=['GET'])
        def get_object():
            if 'address' not in request.args.keys():
                return jsonify({'error': 'the request has no key: address'})
            client = ClientStorageExplorer(request.args['address'])

            id_object = None
            if ('id_object' in request.args.keys()) and (request.args['id_object'] != 'None'):
                id_object = request.args['id_object']

            cur_obj = client.find_object_on_hash(id_object)
            if cur_obj is None:
                return jsonify({'error': f'id_object = {id_object} not found'})

            if cur_obj.is_file():
                hashes = json.loads(client._load_replica(cur_obj.hash))[2]

                def generate_chunk():
                    for hash in hashes:
                        yield client._load_replica(hash)

                return Response(generate_chunk())
            else:
                parent = cur_obj.parent
                if parent:
                    parent_hash = cur_obj.parent.hash
                else:
                    parent_hash = ''
                try:
                    response = client_pool.request(id_client=request.args['address'],
                                                   method='get_occupied')
                except:
                    return jsonify(404)
                dct_files_and_directories = {'parent': parent_hash, 'files': [], 'dirs': [],
                                             'occupied': response['occupied']}
                if not cur_obj == client.root_dir:
                    dct_files_and_directories['dirs'].append({'name': '..', 'id_object': cur_obj.parent.hash})
                for child in cur_obj.get_children():
                    response = client_pool.request(id_client=request.args['address'], method='get_info_object',
                                                   json={'id_object': child.hash})
                    dct_files_and_directories[{FileExplorer: 'files', DirectoryExplorer: 'dirs'}[type(child)]] += \
                        [{'name': child.name, 'id_object': child.hash, 'info': response['info']}]
                return jsonify(dct_files_and_directories)

        app.run(host='0.0.0.0', port=self._port)
