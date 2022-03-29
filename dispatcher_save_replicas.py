import os
import time

from threading import Thread
from utils import get_path, get_size_file, is_ttl_file


class DispatcherSaveReplicas(Thread):
    def __init__(self, fog_nodes_state, server_fn):
        super().__init__()
        self._fog_nodes_state = fog_nodes_state
        self._server_fn = server_fn

    def run(self):
        path = get_path('data/pool/waiting_replicas/')
        while True:
            for directory_path, directory_names, file_names in os.walk(path):
                for file_name in file_names:
                    if file_name.find('.tmp'):
                        continue

                    size = get_size_file(path + file_name)
                    fog_nodes_of_free_size = self._fog_nodes_state.get_of_free_size(size)
                    with open(path + file_name, 'rb') as f:
                        data = f.read()

                    is_save_in_replicas = False
                    for fog_node in fog_nodes_of_free_size:
                        if not self._fog_nodes_state.exist_replica(fog_node, file_name):
                            self._server_fn.request(id_worker=fog_node, method='save_replica', data=data)
                            self._fog_nodes_state.add_hash_replica(fog_node, file_name)
                        is_save_in_replicas = True

                    if not self._fog_nodes_state.is_empty and not fog_nodes_of_free_size:
                        # Сделать находжение коэффициента репликации.
                        # Запись в fog nodes, если нет свободного места в подключенных к пулу нодах
                        pass

                    if is_save_in_replicas and not is_ttl_file(f'data/pool/waiting_replicas/{file_name}'):
                        os.remove(path + file_name)
            time.sleep(0.1)
            pass

