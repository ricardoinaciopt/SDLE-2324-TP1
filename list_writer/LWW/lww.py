import time
import uuid


class ShoppingList:
    def __init__(self):
        self.add_set = {}
        self.remove_set = {}
        self.list_id = uuid.uuid4()

    def add(self, element):
        try:
            if self.add_set.get(element, 0) < time.time():
                self.add_set[element] = time.time()
        except TypeError as error:
            print(str(error))

    def lookup(self, element):
        if element not in self.add_set:
            return False

        if element not in self.remove_set:
            return True

        if self.remove_set[element] < self.add_set[element]:
            return True

        return False

    def remove(self, element):
        try:
            if self.remove_set.get(element, 0) < time.time():
                self.remove_set[element] = time.time()
        except TypeError as error:
            print(str(error))

    def compare(self, other):
        add_subset = set(self.add_set.keys()).issubset(other.add_set.keys())

        remove_subset = set(self.remove_set.keys()).issubset(other.remove_set.keys())

        return add_subset and remove_subset

    def merge(self, other):
        merged_list = ShoppingList()

        merged_list.add_set = {**self.add_set, **other.add_set}

        merged_list.remove_set = {**self.remove_set, **other.remove_set}

        for element, timestamp in self.add_set.items():
            merged_list.add_set[element] = max(merged_list.add_set[element], timestamp)

        for element, timestamp in self.remove_set.items():
            merged_list.remove_set[element] = max(
                merged_list.remove_set[element], timestamp
            )

        return merged_list

    def get_full_list(self):
        list_elements = list(self.add_set.keys() | self.remove_set.keys())
        full_list = []
        for e in list_elements:
            if self.lookup(e):
                full_list.append(e)

        return full_list
