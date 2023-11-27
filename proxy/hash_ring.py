import hashlib


class HashRing:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = {}
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            hash_key = self._hash(f"{node}-{i}")
            self.ring[hash_key] = node

    def remove_node(self, node):
        for i in range(self.replicas):
            hash_key = self._hash(f"{node}-{i}")
            del self.ring[hash_key]

    def lookup_node(self, key):
        if not self.ring:
            return None

        hash_key = self._hash(key)
        ring_keys = list(self.ring.keys())
        ring_keys.sort()

        for ring_key in ring_keys:
            if hash_key <= ring_key:
                return self.ring[ring_key]

        return self.ring[ring_keys[0]]


if __name__ == "__main__":
    # Initial nodes
    nodes = ["node1", "node2", "node3", "node4", "node5"]

    # Create a hash ring with initial nodes
    ring = HashRing(nodes)

    # Key to be mapped to a node
    key = "list_234234"

    # Get the node for the key before removal
    # WE DONT NEED TO HASH THE KEY BEFORE LOOKUP
    node_before_removal = ring.lookup_node(key)
    print(f"The node for key '{key}' is: {node_before_removal}")

    # Remove a node from the hash ring
    add_node = "node6"
    ring.add_node(add_node)
    print(f"Node '{add_node}' has been added from the hash ring.")

    # Get the node for the key after removal
    node_after_removal = ring.lookup_node(key)
    print(f"The node for key '{key}' after removal is: {node_after_removal}")
