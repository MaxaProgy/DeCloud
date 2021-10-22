import socket
from threading import Thread
import json
from queue import Queue


# Отправляем два запроса
# 1 - размер 2
# 2 - бинарные данные data
def _send_request(sock, data):
    request = json.dumps(data)
    sock.send((len(request)).to_bytes(4, "big"))
    sock.send(bytes(request, 'utf-8'))


# Принимаем запрос 1 и 2
def _receive_request(sock):
    length_response = int.from_bytes(sock.recv(4), 'big')
    return json.loads(sock.recv(length_response).decode('utf-8'))


class ClientDCTP(Thread):
    def __init__(self, id_plot):
        Thread.__init__(self)
        self._receiver_thread = None
        self._id = id_plot
        self._socks = {}

    # Устанавливаем соединение
    def connect(self, ip, port):
        for type_connect in ('server to client', 'client to server'):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            _send_request(sock, {'id': self._id, 'type': type_connect})
            self._socks[type_connect] = sock
        # Созданем поток и перенаправляем на отслушку последующего запроса
        self._receiver_thread = Thread(target=self._receiver, args=(self._socks['server to client'],))
        self._receiver_thread.start()

    def request(self, method, data=None):
        # Подготавливаем данные к отправке запроса
        if data:
            _send_request(self._socks['client to server'], {'method': method, 'data': data})
        else:
            _send_request(self._socks['client to server'], {'method': method})

    def _receiver(self, sock):
        # Ждем пока придет запрос
        while True:
            response = _receive_request(sock)
            print('client', response)


class ServerDCTP(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self._clients = {}
        self._dict_methods_call = {}
        self._port = port

        self._queue = Queue()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self._port))
        sock.listen(5)

        # Ждем получение запроса
        while True:
            try:
                client, addr = sock.accept()
                response = _receive_request(client)
                receiver_thread = Thread(target=self._receiver, args=(client,))
                receiver_thread.start()
                # Храним ссылки на потоки, чтобы они не закрылись
                self._clients[response['id']] = self._clients.get(response['id'], {})
                self._clients[response['id']][response['type']] = {'client': client, 'thread': receiver_thread}

            except KeyboardInterrupt:
                sock.close()

    def _receiver(self, sock):
        # Ждем пока придет запрос и вызываем соответствующий метод
        while True:
            response = _receive_request(sock)
            if response['method'] == 'new_transaction':
                self._dict_methods_call['new_transaction'](response['data'])
            else:
                print('server', response)

    def get_id_clients(self):
        # Возвращаем все id клиентов
        return [id_client for id_client in self._clients.keys()]

    def request(self, id_client, method, data=None):
        # Подготавливаем данные к отправке запроса
        if data:
            _send_request(self._clients[id_client]['server to client']['client'], {'method': method, 'data': data})
        else:
            _send_request(self._clients[id_client]['server to client']['client'], {'method': method})

    def method(self, name_method):
        # Декоратор. Храним ссылки на функции методов по их названиям
        def decorator(func):
            self._dict_methods_call[name_method] = func

        return decorator
