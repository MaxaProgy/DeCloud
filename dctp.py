import socket
import time
from threading import Thread, RLock
import json as _json
from utils import print_warning, print_info


def send_status_code(status, status_text):
    return {'status': status, 'status_text': status_text}


class ClientDCTP(Thread):
    def __init__(self, client_name, ip, port, type_connection='duplex', reconnect=False):
        Thread.__init__(self)
        self.reconnect = reconnect
        if type_connection == 'duplex':
            self._type_connection = ['client to server', 'server to client']
        elif type_connection in ['client to server', 'server to client']:
            self._type_connection = [type_connection]
        else:
            raise TypeError('type_connection must be either client to server or server to client or duplex')

        self.lock_obj = RLock()
        self._ip = ip
        self._port = port
        self._client_name = client_name
        self._dict_methods_call = {}
        self._socks = {}
        self._stoping = False
        self._break_stoping = False

    @property
    def client_name(self):
        return self._client_name

    # Принимаем запрос
    def _receive_data(self, sock):
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
    @staticmethod
    def _send_data(sock, json, data):
        json = _json.dumps(json)
        sock.send(len(json).to_bytes(4, "big") + len(data).to_bytes(4, "big") + bytes(json, 'utf-8') + data)

    def stop(self):
        self._stoping = True
        [self._socks[key].close() for key in self._socks]

    # Устанавливаем соединение
    def run(self):
        while not self._stoping:
            try:
                for type_connect in self._type_connection:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self._ip, self._port))
                    json = _json.dumps({'id_worker': self._client_name, 'type': type_connect})
                    sock.send(len(json).to_bytes(4, "big") + bytes(json, 'utf-8'))

                    self._socks[type_connect] = sock

                # Созданем поток и принимаем входящие запросы от сервера
                if "server to client" in self._type_connection:
                    receiver_thread = Thread(target=self._receiver, args=[self._socks['server to client']])
                    receiver_thread.start()
                    receiver_thread.join()
            except:
                if not self.reconnect:
                    break
        if self._stoping:
            print_info(f'Client {self._client_name} disconnect {self._ip}:{self._port}')
        else:
            print(f'Client {self._client_name} connection break.')


    def request(self, method, id_client=None, json={}, data=b''):
        if id_client is None:
            id_client = self.client_name
        # Отправляем запрос серверу и принимаем ответ
        if type(data) != bytes:
            raise Exception('Parameter data is not bytes')
        try:
            json = _json.dumps({'method': method, 'json': json})
        except:
            raise Exception(f'Parameter json as {type(json)} is not parsing to json')

        try:
            self._socks['client to server'].send(len(id_client).to_bytes(4, "big") + bytes(id_client, 'utf-8') +
                                                 len(json).to_bytes(4, "big") + bytes(json, 'utf-8') +
                                                 len(data).to_bytes(4, "big") + data)
        except Exception as e:
            print(96666666666666, e)
        return self._receive_data(self._socks['client to server'])

    def _receiver(self, sock):
        lock_obj = RLock()
        while True:
            # Ждем пока придет запрос от сервера
            try:
                # принимаем длину получаемых данных
                length_json = int.from_bytes(sock.recv(4), 'big')
                with lock_obj:
                    length_data = int.from_bytes(sock.recv(4), 'big')
                    json = _json.loads(sock.recv(length_json).decode('utf-8'))
                    data = sock.recv(length_data)
            except:
                # если обрыв соединения
                break

            # Если в запросе от сервера пришел error
            if 'error' in json.keys():
                self._stoping = True
                raise Exception(json["error"])

            # готовим ответ серверу
            if json['method'] in self._dict_methods_call:
                response = self._dict_methods_call[json['method']](json=json['json'], data=data)
                # если в ответе ни чего нет то создаем ответ
                if type(response) == bytes:
                    data = response
                    response = None

                if response is None:
                    response = {}

                # Дополняем статус возврата, если его нет по умолчанию ОК
                if 'status' not in response.keys():
                    response['status'] = 0
                    response['status_text'] = "success"
            else:
                data = b''
                response['status'] = 100
                response['status_text'] = "not method in request"
            # отправляем ответ серверу
            if not self._stoping:
                self._send_data(sock, response, data)

    def method(self, name_method):
        # Декоратор. Храним ссылки на функции запросов от сервера по их названиям
        def decorator(func):
            self._dict_methods_call[name_method] = func

        return decorator


class ServerDCTP(Thread):
    def __init__(self, port=10_000):
        Thread.__init__(self)
        self.stoping = False
        self.count_current_work = 0
        self._workers = {}
        self._clients = {}
        self._port = port
        self._dict_methods_call = {}
        self.lock_obj = RLock()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self._port < 10_000:
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            try:
                self._sock.bind(('', self._port))
                break
            except:
                if self._port < 10000:
                    raise Exception(f'Error do not start server port {self._port}')
                self._port = (self._port + 1) % 65635
        print_info(f'Server DCTP started port: {self._port}')

    def stop(self):
        self.stoping = True
        while self.count_current_work != 0:

            time.sleep(0.1)
        self._sock.close()

    def run(self):
        self._sock.listen(5)

        # Ждем получение запроса
        while True:
            try:
                worker_sock, _ = self._sock.accept()
                if self.stoping:
                    return
                # получаем длину сообщения
                worker_sock.settimeout(5)
                length_response = int.from_bytes(worker_sock.recv(4), 'big')
                # получаем само сообщение
                response = _json.loads(worker_sock.recv(length_response).decode('utf-8'))
                worker_sock.settimeout(None)

                if response:
                    # проверяем подключен ли клиент уже
                    if response["id_worker"] in self._workers and \
                            response["type"] in self._workers[response["id_worker"]]:
                        self._send_data(worker_sock, json={'error': f'client {response["id_worker"]} already connect'})
                        print_warning(f'client {response["id_worker"]} already connect')
                        print(6666666666666666666666, self._workers[response["id_worker"]])
                        continue
                    else:
                        # проверка на валидность подключения через вызываемую функцию-декоратор connect_valid_client
                        valid_connect = True
                        if "connect_valid_client" in self._dict_methods_call:
                            valid_connect = self._dict_methods_call["connect_valid_client"](
                                json={"id_worker": response["id_worker"]})
                            if type(valid_connect) is not bool:
                                valid_connect = False

                        # регистрируем клиента
                        if valid_connect:
                            if response["id_worker"] not in self._workers.keys():
                                print_info(f'Client "{response["id_worker"]}" connected. port:{self._port}')

                            self._workers[response['id_worker']] = self._workers.get(response['id_worker'], {})
                            self._workers[response['id_worker']][response['type']] = worker_sock

                            if response['type'] == "client to server":
                                receiver_thread = Thread(target=self._receiver,
                                                         args=(worker_sock, response['id_worker']))
                                receiver_thread.start()
                            elif response['type'] == "server to client" and "on_connected" in self._dict_methods_call:
                                self._dict_methods_call["on_connected"](json={"id_worker": response["id_worker"]})
                        else:
                            self._send_data(worker_sock, json={'error': f'client {response["id_worker"]} is not valid'})
                            print_warning(f'client {response["id_worker"]} is not valid')
            except socket.error:
                break
            except Exception as e:
                print(99999999999, e, self._sock)

    @staticmethod
    def _send_data(sock, json={}):
        json = _json.dumps(json)

        sock.send(len(json).to_bytes(4, "big"))
        sock.send(bytes(json, 'utf-8'))

    def _receiver(self, sock, id_worker):
        # Ждем пока придет запрос и вызываем соответствующий метод
        while True:
            try:
                len_id_client = int.from_bytes(sock.recv(4), 'big')
                with self.lock_obj:
                    id_client = sock.recv(len_id_client).decode('utf-8')
                    response = sock.recv(int.from_bytes(sock.recv(4), 'big'))
                    data = sock.recv(int.from_bytes(sock.recv(4), 'big'))
                response = _json.loads(response.decode('utf-8'))
                if self.stoping:
                    return
                response['json']['id_client'] = id_client
                response['json']['id_worker'] = id_worker
                self.count_current_work += 1
                while True:
                    try:
                        response = self._dict_methods_call[response['method']](json=response['json'], data=data)
                        break
                    except:
                        time.sleep(0.1)
                        continue
                self.count_current_work -= 1

                if response is None:
                    response = {}
                response['id_fog_node'] = id_client
                if 'status' not in response.keys():
                    response['status'] = 0
                    response['status_text'] = "success"

                self._send_data(sock, json=response)
            except:
                if id_worker in self._workers:
                    worker = self._workers[id_worker]
                    self._workers.pop(id_worker)
                    [worker[type_sock].close() for type_sock in worker]

                if 'on_disconnected' in self._dict_methods_call:
                    self._dict_methods_call['on_disconnected'](json={"id_worker": id_worker})
                break


    def request(self, id_worker, method, json={}, data=b''):
        # Отправляем запрос клиенту и принимаем ответ
        if id_worker not in self._workers:
            raise Exception(f'Client {id_worker} is not connect')
        if type(data) != bytes:
            raise Exception('Parameter data is not bytes')
        try:
            json = _json.dumps({'method': method, 'json': json})
        except:
            raise Exception(f'Parameter json as {type(json)} is not parsing to json')

        try:
            # отправляем запрос
            sock = self._workers[id_worker]['server to client']
            sock.send(len(json).to_bytes(4, "big") + len(data).to_bytes(4, "big") + bytes(json, 'utf-8') + data)

            # принимаем ответ
            length_json = int.from_bytes(sock.recv(4), 'big')
            with self.lock_obj:
                length_data = int.from_bytes(sock.recv(4), 'big')
                return _json.loads(sock.recv(length_json).decode('utf-8')), sock.recv(length_data).decode('utf-8')
        except:
            # если обрыв соединения
            if id_worker in self._workers:
                worker = self._workers[id_worker]
                self._workers.pop(id_worker)
                [worker[type_sock].close() for type_sock in worker]

            raise Exception(f'Client connection break {id_worker} port {self._port}')


    def method(self, name_method):
        # Декоратор. Храним ссылки на функции методов по их названиям
        def decorator(func):
            self._dict_methods_call[name_method] = func

        return decorator

    @property
    def current_port(self):
        return self._port

    def get_workers(self):
        return tuple(self._workers.keys())

    def get_count_workers(self):
        return len(self._workers)