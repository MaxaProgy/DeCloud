import os
import socket
import time
from threading import Thread, RLock
import json
from wallet import Wallet

_DCTP_STATUS_CODE = {0: 'success',
                     100: 'error'}


def send_status_code(status):
    return {'status': status, 'status text': _DCTP_STATUS_CODE[status]}


class ClientDCTP(Thread):
    def __init__(self, worker_name, ip, port, type_connection='duplex'):
        if type_connection == 'duplex':
            self._type_connection = ['client to server', 'server to client']
        elif type_connection in ['client to server', 'server to client']:
            self._type_connection = [type_connection]
        else:
            raise TypeError('type_connection must be either client to server or server to client or duplex')
        Thread.__init__(self)

        self.lock_obj = RLock()
        self._ip = ip
        self._port = port
        self._worker_name = worker_name
        self._dict_methods_call = {}
        self._socks = {}
        self.connect()

    @staticmethod
    # Принимаем запрос 1 и 2
    def _receive_request(self, sock):
        try:
            length_response = int.from_bytes(sock.recv(4), 'big')
            with self.lock_obj:
                return json.loads(sock.recv(length_response).decode('utf-8'))
        except:
            return

    def _send_request(self, sock, data=None):
        # Отправляем два запроса
        # 1 - размер 2
        # 2 - бинарные данные data
        request = json.dumps(data)

        sock.send(len(request).to_bytes(4, "big"))
        sock.send(bytes(request, 'utf-8'))

    # Устанавливаем соединение
    def connect(self):
        while True:
            try:
                for type_connect in self._type_connection:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self._ip, self._port))
                    self._send_request(sock, {'id': self._worker_name, 'type': type_connect})

                    self._socks[type_connect] = sock
            except:
                print('Нет соединения.')
                time.sleep(1)
            else:
                print(f'Connect with {self._worker_name} ready')
                # Созданем поток и перенаправляем на отслушку последующего запроса
                if "server to client" in self._type_connection:
                    receiver_thread = Thread(target=self._receiver)
                    receiver_thread.start()
                break

    def request(self, id_storage, method, data=None):
        # Подготавливаем данные к отправке запроса

        request = json.dumps({'method': method, 'data': data})

        self._socks['client to server'].send(bytes(id_storage, 'utf-8') + len(request).to_bytes(4, "big"))
        self._socks['client to server'].send(bytes(id_storage, 'utf-8') + bytes(request, 'utf-8'))

        return self._receive_request(self, self._socks['client to server'])

    def _receiver(self):
        # Ждем пока придет запрос
        while True:
            response = self._receive_request(self, self._socks['server to client'])
            if response is None:
                print('Нет соединения.')
                self.connect()
                break
            response = self._dict_methods_call[response['method']](response['data'])
            if response is None:
                response = {}
            if 'status' not in response.keys():
                response['status'] = 0
                response['status text'] = _DCTP_STATUS_CODE[0]
            self._send_request(self._socks['server to client'], response)

    def method(self, name_method):
        # Декоратор. Храним ссылки на функции методов по их названиям
        def decorator(func):
            self._dict_methods_call[name_method] = func

        return decorator


class ServerDCTP(Thread):
    def __init__(self, port=10000):
        Thread.__init__(self)
        self._workers = {}
        self._clients = {}
        self._port = port
        self._dict_methods_call = {}

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                sock.bind(('', self._port))
                break
            except:

                if self._port < 10000:
                    raise Exception(f'Error do not start server port {self._port}')
                self._port = (self._port + 1) % 65635

        sock.listen(5)

        # Ждем получение запроса
        while True:
            try:
                worker_sock, _ = sock.accept()
                response = self._receive_request(worker_sock)
                if response:
                    if response["id"] not in self._workers.keys():
                        print(f'Create {response["id"]} ')
                    if response['type'] == "client to server":
                        receiver_thread = Thread(target=self._receiver, args=(worker_sock, response['id']))
                        receiver_thread.start()
                    self._workers[response['id']] = self._workers.get(response['id'], {})
                    self._workers[response['id']][response['type']] = worker_sock

            except KeyboardInterrupt:
                sock.close()
    @staticmethod
    # Принимаем запрос 1 и 2
    def _receive_request(sock):
        try:
            length_response = int.from_bytes(sock.recv(4), 'big')
        except:
            return
        return json.loads(sock.recv(length_response).decode('utf-8'))

    @staticmethod
    def _send_request(sock, data=None):
        # Отправляем два запроса
        # 1 - размер 2
        # 2 - бинарные данные data

        request = json.dumps(data)

        sock.send(len(request).to_bytes(4, "big"))
        sock.send(bytes(request, 'utf-8'))

    def _receiver(self, sock, id_client):
        # Ждем пока придет запрос и вызываем соответствующий метод
        while True:
            try:
                address_response = sock.recv(40).decode('utf-8')  # address (40 bytes)
                if address_response in self._clients.keys():
                    response = json.loads(sock.recv(self._clients[address_response]).decode('utf-8'))
                    response = self._dict_methods_call[response['method']](response['data'])
                    if response is None:
                        response = {}
                    if 'status' not in response.keys():
                        response['status'] = 0
                        response['status text'] = _DCTP_STATUS_CODE[0]
                    self._clients.pop(address_response)
                    self._send_request(sock, response)

                else:
                    self._clients[address_response] = int.from_bytes(sock.recv(4), 'big')
            except:
                if id_client in self._workers.keys():
                    print(f'{id_client} разорвал соединение')
                    self._workers.pop(id_client)

    def request(self, id_worker, method, data=None):
        # Подготавливаем данные к отправке запроса
        self._send_request(self._workers[id_worker]['server to client'], {'method': method, 'data': data})

    def method(self, name_method):
        # Декоратор. Храним ссылки на функции методов по их названиям
        def decorator(func):
            self._dict_methods_call[name_method] = func

        return decorator

    @property
    def current_port(self):
        return self._port