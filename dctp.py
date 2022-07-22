import socket
import time
from threading import Thread, RLock
import json as _json
from utils import print_warning, print_info


def send_status_code(status, status_text):
    return {'status': status, 'status_text': status_text}

class Request():
    def __init__(self, json, data=b''):
        if 'id_worker' in json:
            self.id_worker = json.pop('id_worker')
        if 'id_client' in json:
            self.id_client = json.pop('id_client')
        if 'method' in json:
            self.method = json.pop('method')
        self.json = json
        self.data = data

class Response():
    def __init__(self, json, data=b''):
        self.status = json.pop('status')
        self.status_text = json.pop('status_text')
        if 'id_worker' in json:
            self.id_worker = json.pop('id_worker')
        if 'id_client' in json:
            self.id_client = json.pop('id_client')
        self.json = json
        self.data = data

class ClientDCTP():
    def __init__(self, client_name, reconnect=False):
        self._type_connection = ['server to client', 'client to server']
        self._lock_obj = RLock()
        self._client_name = client_name
        self._dict_methods_call = {}
        self._socks = {}
        self._stoping = False
        self._connected = False
        self._reconnect = reconnect
        self.receiver_thread = None

    @property
    def client_name(self):
        return self._client_name

    def _close_socks(self):
        self._connected = False
        for type_connect in self._socks:
            try:
                self._socks[type_connect].close()
            except:
                pass

    def disconnect(self):
        self._stoping = True
        self._close_socks()
        while self.receiver_thread and self.receiver_thread.is_alive():
            time.sleep(0.1)

    def is_connected(self):
        return self._connected

    def _reconnect_loop(self):
        while not self._stoping:
            if not self.is_connected():
                self._connect()
            time.sleep(1)

    def _connect(self):
        try:
            for type_connect in self._type_connection:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self._ip, self._port))
                # регистрируем клиента
                json = _json.dumps({'id_worker': self._client_name, 'type': type_connect})
                sock.send(len(json).to_bytes(4, "big") + bytes(json, 'utf-8'))

                # ждем подтверждения регистрации от сервера
                data = self._recv_data(sock)
                if data[0]['status'] != 0:
                    return False

                self._socks[type_connect] = sock
                if type_connect == 'server to client':
                    # Созданем поток и принимаем входящие запросы от сервера
                    self.receiver_thread = Thread(target=self._receiver, args=[sock])
                    self.receiver_thread.start()
            self._connected = True
        except:
            pass

    # Устанавливаем соединение
    def connect(self, ip, port):
        self.disconnect()
        self._stoping = False
        self._ip = ip
        self._port = port
        if self._reconnect:
            reconnect_thread = Thread(target=self._reconnect_loop)
            reconnect_thread.start()
        else:
            self._connect()

    def _send_data(self, sock, id_client, json, data):
       sock.send(len(id_client).to_bytes(4, "big") + bytes(id_client, 'utf-8') +
                  len(json).to_bytes(4, "big") + bytes(json, 'utf-8') + len(data).to_bytes(4, "big") + data)

    def _recv_data(self, sock):
        try:
            # принимаем данные
            length_json = int.from_bytes(sock.recv(4), 'big')
            length_data = int.from_bytes(sock.recv(4), 'big')
            return _json.loads(sock.recv(length_json).decode('utf-8')), sock.recv(length_data).decode('utf-8')
        except Exception as e:
            print_info(324546546, e)
            return

    def request(self, method, id_client=None, json={}, data=b''):
        if id_client is None:
            id_client = self.client_name
        if type(data) != bytes:
            return Response(send_status_code(100, 'Parameter data is not bytes'))

        json['method'] = method
        json = _json.dumps(json)

        try:
            with self._lock_obj:
                sock = self._socks['client to server']

                # Отправляем запрос серверу
                self._send_data(sock, id_client, json, data)

                # Принимаем запрос от сервера
                return Response(*self._recv_data(sock))
        except:
            self._close_socks()
            return Response(send_status_code(100, 'Request break connection'))

    def _receiver(self, sock):
        while True:
            try:
                # Ждем пока придет запрос от сервера
                request = self._recv_data(sock)

                if request is None:
                    print(f'Client {self._client_name} connection break.')
                    return

                if self._stoping:
                    break
                request = Request(*request)

                data = b''
                if request.method in self._dict_methods_call:
                    response = self._dict_methods_call[request.method](request)


                    if request.method == 'stop':
                        break

                    # готовим ответ серверу
                    if type(response) == bytes:
                        data = response
                        response = None

                    # Дополняем статус возврата, если его нет по умолчанию 0.
                    if response is None or 'status' not in response.keys():
                        response = send_status_code(0, "success")
                else:
                    response = send_status_code(100, "not method in request")

                # отправляем ответ серверу
                json = _json.dumps(response)
                sock.send(len(json).to_bytes(4, "big") + len(data).to_bytes(4, "big") + bytes(json, 'utf-8') + data)
            except Exception as e:
                print_info(32323323232323, e)
                pass
        print_info(f'Client {self._client_name} disconnect {self._ip}:{self._port}')
        self._close_socks()

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
        self._sock.listen(100)

    def stop(self):
        self.stoping = True
        while self.count_current_work != 0:
            time.sleep(0.1)
        self._sock.close()

    def close_worker(self, id_worker):
        worker = self._workers.pop(id_worker)
        for type_sock in worker:
            try:
                worker[type_sock].close()
            except:
                pass

    def run(self):
        while True:
            try:
                response = None
                # Ждем подключения клиента
                worker_sock, _ = self._sock.accept()
                if self.stoping:
                    return
                worker_sock.settimeout(5)
                try:
                    # получаем длину сообщения
                    length_response = int.from_bytes(worker_sock.recv(4), 'big')
                    # получаем само сообщение
                    request = _json.loads(worker_sock.recv(length_response).decode('utf-8'))
                except socket.timeout:
                    worker_sock.close()
                    continue
                if not request:
                    worker_sock.close()

                try:
                    # проверяем подключен ли клиент уже
                    if request["id_worker"] in self._workers and \
                            request["type"] in self._workers[request["id_worker"]]:
                        self._send_data(worker_sock, send_status_code(110, f'client already connect'))
                        print_warning(f'client {request["id_worker"]} already connect')
                        print(6666666666666666666666, self._workers[request["id_worker"]])

                        self.close_worker(request["id_worker"])
                        #continue
                    worker_sock.settimeout(None)
                    # проверка на валидность подключения через вызываемую функцию-декоратор connect_valid_client
                    valid_connect = True
                    if "connect_valid_client" in self._dict_methods_call:
                        valid_connect = self._dict_methods_call["connect_valid_client"](
                            Request(json={"id_worker": request["id_worker"]}))
                        if type(valid_connect) is not bool:
                            raise Exception(f'Method "connect_valid_client" return {type(valid_connect)} '
                                            f'should be boolean argument')
                    # регистрируем клиента
                    if valid_connect:
                        if request["id_worker"] not in self._workers.keys():
                            print_info(f'Client "{request["id_worker"]}" connected. port:{self._port}')

                        self._workers[request['id_worker']] = self._workers.get(request['id_worker'], {})
                        self._workers[request['id_worker']][request['type']] = worker_sock

                        if request['type'] == "client to server":
                            receiver_thread = Thread(target=self._receiver,
                                                     args=(worker_sock, request['id_worker']))
                            receiver_thread.start()

                            if "on_connected" in self._dict_methods_call:
                                self._dict_methods_call["on_connected"](Request(json={"id_worker":
                                                                                          request["id_worker"]}))

                        self._send_data(worker_sock, send_status_code(0, "success"))
                    else:
                        self._send_data(worker_sock,
                                        send_status_code(120, f'client {request["id_worker"]} is not valid'))
                        print_warning(f'client {request["id_worker"]} is not valid')

                except socket.error:
                    print(99999999999, worker_sock)
                    if request and "id_worker" in request and request["id_worker"] in self._workers:
                        self.close_worker(request["id_worker"])

            except Exception as e:
            #except socket.error:
                if self.stoping:
                    break
                print(888888888888, self._sock)
                print(888888888888, e)

    @staticmethod
    def _send_data(sock, json, data=b''):
        json = _json.dumps(json)
        sock.send(len(json).to_bytes(4, "big") + len(data).to_bytes(4, "big") + bytes(json, 'utf-8') + data)

    def _receiver(self, sock, id_worker):
        lock_obj = RLock()
        # Ждем пока придет запрос и вызываем соответствующий метод
        while True:
            try:
                len_id_client = int.from_bytes(sock.recv(4), 'big')
                with lock_obj:
                    id_client = sock.recv(len_id_client).decode('utf-8')
                    request = sock.recv(int.from_bytes(sock.recv(4), 'big'))
                    data = sock.recv(int.from_bytes(sock.recv(4), 'big'))
                request = _json.loads(request.decode('utf-8'))

                if self.stoping:
                    return
                request.update({'id_worker': id_worker, 'id_client': id_client})

                self.count_current_work += 1
                response = self._dict_methods_call[request['method']](Request(json=request, data=data))
                self.count_current_work -= 1

                if response is None:
                    response = {}
                response.update({'id_worker': id_worker, 'id_client': id_client})
                if 'status' not in response.keys():
                    response.update(send_status_code(0, "success"))

                self._send_data(sock, json=response)
            except Exception as e:
                print_info(3333333333333333333333333, e)
                if id_worker in self._workers:
                    self.close_worker(id_worker)
                print_info(5665656665665)
                if 'on_disconnected' in self._dict_methods_call:
                    self._dict_methods_call['on_disconnected'](Request(json={"id_worker": id_worker}))
                print_info(787878787878878)
                break

    def request(self, id_worker, method, json={}, data=b'', timeout=10):
        # Отправляем запрос клиенту и принимаем ответ
        if id_worker not in self._workers:
            return Response(send_status_code(100, f'Client {id_worker} is not connect'))

        if type(data) != bytes:
            return Response(send_status_code(100, 'Parameter data is not bytes'))

        json['method'] = method
        json = _json.dumps(json)

        try:
            # отправляем запрос
            sock = self._workers[id_worker]['server to client']
            with self.lock_obj:
                sock.send(len(json).to_bytes(4, "big") + len(data).to_bytes(4, "big") + bytes(json, 'utf-8') + data)

                # принимаем ответ
                sock.settimeout(timeout)
                length_json = int.from_bytes(sock.recv(4), 'big')
                length_data = int.from_bytes(sock.recv(4), 'big')
                response = Response(_json.loads(sock.recv(length_json).decode('utf-8')),
                                    sock.recv(length_data).decode('utf-8'))
                sock.settimeout(None)
                return response
        except Exception as e:
            print(33333333333333333333333333333333333333333333333333333333333333333333333333333333, e)
            # если обрыв соединения
            if id_worker in self._workers:
                self.close_worker(id_worker)
            #raise Exception(f'Client connection break {id_worker} port {self._port}')
            return Response(send_status_code(100, 'Request break connection'))


    def method(self, name_method: str):
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