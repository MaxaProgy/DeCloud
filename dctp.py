import socket
import time
from threading import Thread
import json
from wallet import Wallet

_DCTP_STATUS_CODE = {0: 'success',
                     100: 'error'}


def send_status_code(status):
    return {'status': status, 'status text': _DCTP_STATUS_CODE[status]}


class MixinDCTP:
    def __init__(self):
        pass

    @staticmethod
    # Принимаем запрос 1 и 2
    def _receive_request(sock):
        try:
            length_response = int.from_bytes(sock.recv(4), 'big')
        except:
            return None
        return json.loads(sock.recv(length_response).decode('utf-8'))

    @staticmethod
    def _send_request(sock, data=None):
        # Отправляем два запроса
        # 1 - размер 2
        # 2 - бинарные данные data
        request = json.dumps(data)
        sock.send((len(request)).to_bytes(4, "big"))
        sock.send(bytes(request, 'utf-8'))


class ClientDCTP(MixinDCTP, Thread):
    def __init__(self, private_key, type_connection='=='):
        if type_connection == 'duplex':
            self._type_connection = ['client to server', 'server to client']
        elif type_connection in ['client to server', 'server to client']:
            self._type_connection = [type_connection]
        else:
            raise TypeError('type_connection must be either client to server or server to client or duplex')
        MixinDCTP.__init__(self)
        Thread.__init__(self)
        self._receiver_thread = None
        self._ip = None
        self._port = None
        self._private_key = private_key
        self._socks = {}

    # Устанавливаем соединение
    def connect(self, ip, port):
        self._ip = ip
        self._port = port
        while True:
            try:
                for type_connect in self._type_connection:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((ip, port))
                    self._send_request(sock, {'id': Wallet(self._private_key).address, 'type': type_connect})
                    self._socks[type_connect] = sock
            except:
                print('Нет соединения.')
                time.sleep(1)
            else:
                print('Соединение с сервером установлено')
                # Созданем поток и перенаправляем на отслушку последующего запроса
                self._receiver_thread = Thread(target=self._receiver)
                self._receiver_thread.start()
                break

    def request(self, method, data=None):
        # Подготавливаем данные к отправке запроса
        self._send_request(self._socks['client to server'], {'method': method, 'data': data})
        return self._receive_request(self._socks['client to server'])

    def _receiver(self):
        # Ждем пока придет запрос
        while True:
            response = self._receive_request(self._socks['server to client'])
            if response is None:
                print('Нет соединения.')
                self.connect(self._ip, self._port)
                break


class ServerDCTP(MixinDCTP, Thread):
    def __init__(self, port):
        MixinDCTP.__init__(self)
        Thread.__init__(self)
        self._clients = {}
        self._dict_methods_call = {}
        self._port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self._port))
        sock.listen(5)

        # Ждем получение запроса
        while True:
            try:
                client, addr = sock.accept()
                response = self._receive_request(client)
                if response:
                    if response["id"] not in self._clients.keys():
                        print(f'Подключился клиент {response["id"]}')
                    receiver_thread = Thread(target=self._receiver, args=(client, response['id']))
                    receiver_thread.start()
                    # Храним ссылки на потоки, чтобы они не закрылись
                    self._clients[response['id']] = self._clients.get(response['id'], {})
                    self._clients[response['id']][response['type']] = {'client': client, 'thread': receiver_thread}

            except KeyboardInterrupt:
                sock.close()

    def _receiver(self, sock, id_client):
        # Ждем пока придет запрос и вызываем соответствующий метод
        while True:
            response = self._receive_request(sock)
            if response is None:
                if id_client in self._clients.keys():
                    print(f'Клиент {id_client} разорвал соединение')
                    self._clients.pop(id_client)
                break
            response = self._dict_methods_call[response['method']](response['data'])
            if response is None:
                response = {}
            if 'status' not in response.keys():
                response['status'] = 0
                response['status text'] = _DCTP_STATUS_CODE[0]
            self._send_request(sock, response)

    def get_id_clients(self):
        # Возвращаем все id клиентов
        return [id_client for id_client in self._clients.keys()]

    def request(self, id_client, method, data=None):
        # Подготавливаем данные к отправке запроса
        self._send_request(self._clients[id_client]['server to client']['client'], {'method': method, 'data': data})

    def method(self, name_method):
        # Декоратор. Храним ссылки на функции методов по их названиям
        def decorator(func):
            self._dict_methods_call[name_method] = func

        return decorator
