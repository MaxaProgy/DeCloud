# -*- coding: utf-8 -*

from queue import Queue
from time import sleep
from datetime import datetime
import hashlib
import json
import os
from threading import Thread

from storage import BaseStorage, SIZE_REPLICA
from flask import Flask, request, jsonify, make_response
from wallet import sign_verification, pub_to_address

SESSION_TIME_LIFE = 24 * 60 * 60


class FileFS:
    def __init__(self, name, hash):
        self._name = name
        self._hash = hash

    @property
    def name(self):
        return self._name

    @property
    def hash(self):
        return self._hash

    def is_file(self):
        # Проверяем на файл ли это
        return type(self) == FileFS


class DirectoryFS:
    def __init__(self, name, hash, parent):
        self._name = name
        self._hash = hash
        self._children = []
        self._parent = parent

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
        return type(self) == FileFS


class CloudFS(BaseStorage):
    # Файловая система
    def __init__(self, public_key):
        BaseStorage.__init__(self)

        self._id_storage = pub_to_address(public_key)
        # Создание корневной - главной директории

        self._root_dir = DirectoryFS(self._id_storage, None, None)

        self._load_state()

    @property
    def root_dir(self):
        return self._root_dir

    def _load_state(self):
        path = self.get_path(self._id_storage, 'state.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                hashes_fs = json.loads(f.read())
            for hash in hashes_fs:  # Проходим по всем
                info_params_obj = json.loads(self._load_replica(hash))  # Формируем json из бинарных данных файла
                if len(info_params_obj) == 3:  # Если файл
                    file = FileFS(info_params_obj[1], hash)  # Создаем файл
                    # Находим папку и добавляем к ней в качестве child - файл
                    self.find_object_on_hash(info_params_obj[0]).add_child(file)
                else:  # если папка
                    parent = self.find_object_on_hash(info_params_obj[0])  # Находим папку
                    # Добавляем к ней в качестве child - файл
                    child = DirectoryFS(info_params_obj[1], hash, parent)
                    parent.add_child(child)

    def save_state(self):
        from queue import Queue
        task_queue = Queue()
        task_queue.put(self.root_dir)  # Очаредь всех вершин графа
        hashes_fs = [self.root_dir.hash]  # Список хэшей-путей к файлам
        while not task_queue.empty():
            current_obj = task_queue.get()  # Забираем объект
            if not current_obj.is_file():
                # Если файл, то добавляем всех его children в очаредь вершин графа и
                # сохраняем в спиок хэши-пути к файлам
                [task_queue.put(child) for child in current_obj.get_children()]
                hashes_fs += [child.hash for child in current_obj.get_children()]

        with open(self.get_path(self.id_storage, 'state.json'), 'w') as f:
            # Сохраняем в файл все хэши к файлам
            f.write(json.dumps(hashes_fs[1:]))  # первый в списке - текущая папка

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

    @staticmethod
    def get_path(*args):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'cloud', *args)

    def make_dir(self, parent, name):
        # Создание папки в файловой системе
        hash = self._save_replica(bytes(json.dumps([parent.hash, name]), 'utf-8'))
        new_dir = DirectoryFS(name, hash, parent)
        parent.add_child(new_dir)
        self.save_state()
        return hash

    def save_file(self, parent, file_name, file_data):
        # Создание нового файла в файловой системе

        len_data = len(file_data)

        hashes = [self._save_replica(file_data[SIZE_REPLICA * count: SIZE_REPLICA * (count + 1)])
                  for count in range(int(len_data / SIZE_REPLICA) + (len_data % SIZE_REPLICA > 0))]
        hash_file = self._save_replica(bytes(json.dumps([parent.hash, file_name, hashes]), 'utf-8'))
        file = FileFS(file_name, hash_file)
        parent.add_child(file)
        self.save_state()
        return hash_file

    def load_file(self, hash):
        hashes = json.loads(self._load_replica(hash))[2]
        return b''.join([self._load_replica(hash) for hash in hashes])


class ClientCloud:
    def __init__(self, port=80):
        self._port = port
        self._session_keys = {}
        path = CloudFS.get_path('temp')
        if not os.path.exists(path):
            os.mkdir(path)

        self.delete_file_queue = Queue()
        self.delete_file_thread = Thread(target=self.delete_file)
        self.delete_file_thread.start()

    def delete_file(self):
        while True:
            if not self.delete_file_queue.empty():
                path = self.delete_file_queue.get()
                while True:
                    try:
                        os.remove(path)
                        break
                    except:
                        sleep(1)
            sleep(10)

    def run(self):

        app = Flask(__name__)

        @app.route('/', methods=['GET'])
        def main():
            return "Привет, Decloud"

        @app.route('/<string:id_decloud>', methods=['GET'])
        def user_cloud(id_decloud):
            client = CloudFS(id_decloud)
            current_dir = client.find_object_on_hash(None)
            return  " ".join([child.name for child in current_dir.get_children()])

        @app.route('/api/save_file', methods=['POST'])
        def save_file():
            # Добавляем файл в файловую сиситему
            data = dict(request.args)
            if not all([key in data.keys() for key in ['id_decloud', 'file_name', 'file_hash', 'sign']]):
                return jsonify({'error': 'required parameters are not specified: id_decloud, file, sign'})

            sign = data.pop('sign')
            if not sign_verification(data=data, sign=sign, public_key=data['id_decloud']):
                return jsonify({'error': 'signature is not valid'})

            if data['file_hash'] != hashlib.sha3_256(request.data).hexdigest():
                return jsonify({'error': 'hash file is not valid'})

            client = CloudFS(data['id_decloud'])
            current_dir = client.find_object_on_hash(None)
            if 'id_current_dir' in data.keys():
                current_dir = client.find_object_on_hash(data['id_current_dir'])

            if data['file_name'] in [child.name for child in current_dir.get_children() if child.is_file()]:
                return jsonify({'error': f'the current object already has the given name {data["file_name"]}'})

            hash_file = client.save_file(current_dir, data['file_name'], request.data)
            return jsonify(hash_file)

        @app.route('/api/make_dir', methods=['GET'])
        def make_dir():
            data = request.json
            if not all([key in data.keys() for key in ['id_decloud', 'name', 'sign']]):
                return jsonify({'error': 'required parameters are not specified: id_decloud, name, sign'})

            sign = data.pop('sign')
            if not sign_verification(data=data, sign=sign, public_key=data['id_decloud']):
                return jsonify({'error': 'signature is not valid'})

            if data['name'] == '..' or '/' in data['name']:
                return jsonify({'error': 'invalid characters in name'})

            client = CloudFS(data['id_decloud'])
            current_dir = client.find_object_on_hash(None)
            if 'id_current_dir' in data.keys():
                current_dir = client.find_object_on_hash(data['id_current_dir'])

            name = data['name']
            if name in [child.name for child in current_dir.get_children() if not child.is_file()]:
                return jsonify({'error': f'the current object already has the given name {name}'})

            return jsonify(client.make_dir(current_dir, name))

        @app.route('/api/get_object', methods=['GET'])
        def get_object():
            if 'id_decloud' not in request.args.keys():
                return jsonify({'error': 'the request has no key: id_decloud'})
            client = CloudFS(request.args['id_decloud'])

            id_object = None
            if 'id_object' in request.args.keys():
                id_object = request.args['id_object']

            cur_obj = client.find_object_on_hash(id_object)
            if cur_obj is None:
                return jsonify({'error': f'id_object = {id_object} not found'})

            if cur_obj.is_file():
                response = make_response(client.load_file(cur_obj.hash))
                response.headers.set('Content-Type', 'application/octet-stream')
                return response
            else:
                parent = cur_obj.parent
                if parent:
                    parent_hash = cur_obj.parent.hash
                else:
                    parent_hash = ''

                dct_files_and_directories = {'parent': parent_hash, 'files': [], 'dirs': []}
                for child in cur_obj.get_children():
                    dct_files_and_directories[{FileFS: 'files', DirectoryFS: 'dirs'}[type(child)]] += \
                        [{'name': child.name, 'id_object': child.hash}]

                return jsonify(dct_files_and_directories)

        app.run(host='127.0.0.1', port=self._port)


if __name__ == '__main__':
    client = ClientCloud()
    client.run()
