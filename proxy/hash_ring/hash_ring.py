import hashlib
import os


class HashRing:
    def __init__(self, nodes=None, virtual_nodes=3, replicas=2):
        self.virtual_nodes = virtual_nodes
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

        if nodes:
            self.generate_ring(nodes)

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def generate_ring(self, nodes):
        for node in nodes:
            for i in range(self.virtual_nodes):
                hash_key = self._hash(f"{node}-{i}")
                self.ring[hash_key] = node
                self.colorize_text(f"HR> ADDED {node} [VN {i+1}] ({hash_key})\n")
                self.sorted_keys.append(hash_key)

        self.sorted_keys.sort()

    def add_node(self, node):
        for i in range(self.virtual_nodes):
            hash_key = self._hash(f"{node}-{i+1}")
            self.ring[hash_key] = node
            self.colorize_text(f"HR> ADDED {node} [VN {i+1}] ({hash_key})\n")
            self.sorted_keys.append(hash_key)

    def remove_node(self, node):
        keys_to_remove = []
        for i in range(self.virtual_nodes):
            hash_key = self._hash(f"{node}-{i}")
            if hash_key in self.ring:
                keys_to_remove.append(hash_key)
                self.colorize_text(f"HR> REMOVED {node} [VN {i+1}] ({hash_key})\n")

        next_node_index = (self.sorted_keys.index(keys_to_remove[-1]) + 1) % len(
            self.sorted_keys
        )
        next_node = self.sorted_keys[next_node_index]

        source_location = f"server_{node}"
        destination_location = f"server_{next_node}"
        if os.path.exists(source_location):
            os.makedirs(destination_location, exist_ok=True)
            files = os.listdir(source_location)
            for file in files:
                source_path = os.path.join(source_location, file)
                destination_path = os.path.join(destination_location, file)
                shutil.move(source_path, destination_path)

        for key in keys_to_remove:
            self.sorted_keys.remove(key)

        new_ring = {}
        for key in self.sorted_keys:
            new_ring[key] = self.ring[key]

        self.ring = new_ring

    def lookup_node(self, key):
        if not self.ring:
            return None

        hash_key = self._hash(key)

        for ring_key in self.sorted_keys:
            if hash_key < ring_key:
                return self.ring[ring_key]

        return self.ring[self.sorted_keys[0]]

    def get_replica_nodes(self, key):
        if not self.ring:
            return None

        hash_key = self._hash(key)

        key_index = None
        for i, ring_key in enumerate(self.sorted_keys):
            if hash_key < ring_key:
                key_index = i
                break

        if key_index is None:
            key_index = 0

        previous_nodes = []
        for i in range(1, self.replicas + 1):
            prev_index = (key_index - i) % len(self.sorted_keys)
            previous_nodes.append(self.ring[self.sorted_keys[prev_index]])

        return tuple(previous_nodes)

    def get_responsible_nodes(self):
        responsible_nodes = {}
        self.sorted_keys.sort()
        for i in range(len(self.sorted_keys)):
            start_key = self.sorted_keys[i]
            end_key = self.sorted_keys[(i + 1) % len(self.sorted_keys)]
            node = self.ring[start_key]
            key_range = (start_key, end_key)
            responsible_nodes.setdefault(node, []).append(key_range)

        return responsible_nodes

    def print_key_ranges(self, index=False):
        responsible_nodes = self.get_responsible_nodes()
        self.colorize_text(f"HR> ACTIVE NODES: {len(responsible_nodes)}\n")
        for node, key_ranges in responsible_nodes.items():
            formatted_ranges = []
            for start_key, end_key in key_ranges:
                if index:
                    start_key = self.sorted_keys.index(start_key)
                    end_key = self.sorted_keys.index(end_key)
                formatted_ranges.append((start_key, end_key))
            self.colorize_text(f"HR> {node} KEY RANGES: {formatted_ranges}\n")

    def colorize_text(self, text):
        prefix = text[:3]

        switch = {
            "P> ": "\033[95m" + text + "\033[0m",  # Purple color
            "C> ": "\033[94m" + text + "\033[0m",  # Blue color
            "S> ": "\033[92m" + text + "\033[0m",  # Green color
            "HR>": "\033[91m" + text + "\033[0m",  # Red color
        }

        colored_text = switch.get(prefix, text)
        print(colored_text)
