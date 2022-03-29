from fog_node import SIZE_REPLICA, COUNT_REPLICAS_IN_FOG_NODE


class FogNodesState:
    def __init__(self):
        self._fog_nodes = {}

    def add(self, id_fog_node, data):
        self._fog_nodes[id_fog_node] = data

    def delete(self, id_fog_node):
        if id_fog_node in self._fog_nodes:
            self._fog_nodes.pop(id_fog_node)

    def add_hash_replica(self, id_fog_node, hash):
        self._fog_nodes[id_fog_node]['hash_replicas'].append(hash)

    def del_hash_replica(self, id_fog_node, hash):
        index = self._fog_nodes[id_fog_node]['hash_replicas'].index(hash)
        if index != -1:
            self._fog_nodes[id_fog_node]['hash_replicas'].pop(index)

    def find_hash_replica(self, hash):
        return [key for key, item in self._fog_nodes if hash in item['hash_replicas']]

    def get_size(self, id_fog_node):
        return self._fog_nodes[id_fog_node]['size_fog_node']

    def get_of_free_size(self, size):
        return [key for key, item in self._fog_nodes.items()
                if item['size_fog_node'] + size <= SIZE_REPLICA * COUNT_REPLICAS_IN_FOG_NODE]

    def exist_replica(self, id_fog_node, hash):
        return hash in self._fog_nodes[id_fog_node]['hash_replicas']

    @property
    def is_empty(self):
        return self._fog_nodes == {}
