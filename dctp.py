import socket
import time
from threading import Thread, RLock
import json as _json

from utils import print_warning, print_info

_DCTP_STATUS_CODE = {0: 'success',
                     100: 'error'}


def send_status_code(status):
    return {'status': status, 'status text': _DCTP_STATUS_CODE[status]}


class ClientDCTP(Thread):
    def __init__(self, worker_name, ip, port, type_connection='duplex'):
        Thread.__init__(self)

        if type_connection == 'duplex':
            self._type_connection = ['client to server', 'server to client']
        elif type_connection in ['client to server', 'server to client']:
            self._type_connection = [type_connection]
        else:
            raise TypeError('type_connection must be either client to server or server to client or duplex')

        self.lock_obj = RLock()
        self._ip = ip
        self._port = port
        self._worker_name = worker_name
        self._dict_methods_call = {}
        self._socks = {}
        self._stoping = False
        self._ready = False

    @staticmethod
    # Принимаем запрос
    def _receive_request(self, sock):
        try:
            # принимаем длину получаемых данных
            length_response = int.from_bytes(sock.recv(4), 'big')
            with self.lock_obj:
                # принимаем данные
                return _json.loads(sock.recv(length_response).decode('utf-8'))
        except:
            # если обрыв соединения
            return

    # Отправляем запрос серверу
    def _send_request(self, sock, data=None):
        request = _json.dumps(data)
        # jngh
        sock.send(len(request).to_bytes(4, "big"))
        sock.send(bytes(request, 'utf-8'))

    def stop(self):
        self._stoping = True
        self._socks = None

    # Устанавливаем соединение
    def run(self):
        while not self._stoping:
            try:
                for type_connect in self._type_connection:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self._ip, self._port))
                    self._send_request(sock, {'worker_id': self._worker_name, 'type': type_connect})

                    self._socks[type_connect] = sock

                print(f'Client connected to {self._worker_name}')
                self._ready = True
                # Созданем поток и принимаем входящие запросы от сервера
                if "server to client" in self._type_connection:
                    receiver_thread = Thread(target=self._receiver)
                    receiver_thread.start()
                    receiver_thread.join()
            except:
                print(f'Нет соединения {self._worker_name}.')
                time.sleep(1)

        print_info(f'{self._worker_name} is stoping')


    def request(self, id_fog_node, method, data=b'', json={}):
        # Подготавливаем данные к отправке запроса
        request = _json.dumps({'method': method, 'json': json})
        while True:
            try:
                self._socks['client to server'].send(bytes(id_fog_node, 'utf-8') + len(request).to_bytes(4, "big") \
                                                     + len(data).to_bytes(4, "big"))
                self._socks['client to server'].send(bytes(id_fog_node, 'utf-8') + bytes(request, 'utf-8') + data)
                break
            except:
                pass
            time.sleep(0.1)

        return self._receive_request(self, self._socks['client to server'])

    def _receiver(self):
        while True:
            # Ждем пока придет запрос от сервкра
            response = self._receive_request(self, self._socks['server to client'])

            # Если произошел сброс соединения
            if not response:
                if not self._stoping:
                    print(f'Нет соединения {self._worker_name}.')
                    time.sleep(0.1)
                break

            # Если в запросе от сервера пришел error
            if 'error' in response.keys():
                self._stoping = True
                raise Exception(response["error"])

            # готовим ответ серверу
            response = self._dict_methods_call[response['method']](response['data'])

            # если в ответе ни чего нет то создаем ответ
            if response is None:
                response = {}

            # Дополняем статус возврата, если его нет по умолчанию ОК
            if 'status' not in response.keys():
                response['status'] = 0
                response['status text'] = _DCTP_STATUS_CODE[0]

            # отправляем ответ серверу
            self._send_request(self._socks['server to client'], response)

    def method(self, name_method):
        # Декоратор. Храним ссылки на функции запросов от сервера по их названиям
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

                # получаем длину сообщения
                worker_sock.settimeout(5)
                length_response = int.from_bytes(worker_sock.recv(4), 'big')
                # получаем само сообщение
                response = _json.loads(worker_sock.recv(length_response).decode('utf-8'))
                worker_sock.settimeout(None)

                if response:
                    # проверяем подключен ли клиент уже
                    if response["worker_id"] in self._workers.keys() and \
                            response["type"] in self._workers[response["worker_id"]].keys():
                        self._send_request(worker_sock, {'error': f'client {response["worker_id"]} already connect'})
                        print_warning(f'client {response["worker_id"]} already connect')
                    else:
                        # проверка на валидность подключения через вызываемую функцию-декоратор connect_valid_client
                        try:
                            valid_connect = self._dict_methods_call["connect_valid_client"](json={"address": response["worker_id"]})
                            if type(valid_connect)  is not bool:
                                valid_connect = False
                        except KeyError as e:
                            if 'connect_valid_client' in e.args:
                                valid_connect = True

                        # регистрируем клиента
                        if valid_connect:
                            if response["worker_id"] not in self._workers.keys():
                                print_info(f'Server "{response["worker_id"]}" started')

                            self._workers[response['worker_id']] = self._workers.get(response['worker_id'], {})
                            self._workers[response['worker_id']][response['type']] = worker_sock

                            if response['type'] == "client to server":
                                receiver_thread = Thread(target=self._receiver, args=(worker_sock, response['worker_id']))
                                receiver_thread.start()
                        else:
                            self._send_request(worker_sock, {'error': f'client {response["worker_id"]} is not valid'})
                            print_warning(f'client {response["worker_id"]} is not valid')
            except KeyboardInterrupt:
                sock.close()

    @staticmethod
    def _send_request(sock, data=None):
        # Отправляем два запроса
        # 1 - размер 2
        # 2 - бинарные данные data

        request = _json.dumps(data)
        sock.send(len(request).to_bytes(4, "big"))
        sock.send(bytes(request, 'utf-8'))

    def _receiver(self, sock, worker_id):
        # Ждем пока придет запрос и вызываем соответствующий метод
        while True:
            try:
                #получаем
                address_response = sock.recv(40).decode('utf-8')  # address (40 bytes)
                if address_response in self._clients.keys():
                    response = _json.loads(sock.recv(self._clients[address_response]['json']).decode('utf-8'))
                    response['json']['address'] = address_response
                    response['json']['worker_id'] = worker_id

                    data = sock.recv(self._clients[address_response]['data'])
                    while True:
                        try:
                            response = self._dict_methods_call[response['method']](json=response['json'], data=data)
                            break
                        except:
                            pass
                        time.sleep(0.1)

                    if response is None:
                        response = {}
                    response['id_fog_node'] = address_response
                    if 'status' not in response.keys():
                        response['status'] = 0
                        response['status text'] = _DCTP_STATUS_CODE[0]
                    self._clients.pop(address_response)
                    self._send_request(sock, response)
                else:
                    self._clients[address_response] = {'json': int.from_bytes(sock.recv(4), 'big'),
                                                       'data': int.from_bytes(sock.recv(4), 'big')}
            except Exception as e:
                if worker_id in self._workers.keys():
                    print(f'{worker_id} разорвал соединение')
                    sock.close()
                    self._workers.pop(worker_id)

                break

    def request(self, id_worker, method, data=None):
        # Подготавливаем данные к отправке запроса
        while True:
            try:
                self._send_request(self._workers[id_worker]['server to client'], {'method': method, 'data': data})
                break
            except:
                time.sleep(0.1)


    def method(self, name_method):
        # Декоратор. Храним ссылки на функции методов по их названиям
        def decorator(func):
            self._dict_methods_call[name_method] = func

        return decorator

    @property
    def current_port(self):
        return self._port

    def get_workers(self):
        return self._workers.keys()
