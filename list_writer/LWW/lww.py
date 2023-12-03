import time
import uuid
import json
import os


class ShoppingList:
    def __init__(self):
        self.add_set = {}
        self.remove_set = {}
        self.uuid = uuid.uuid4()

    def add(self, item):
        item_id = item["id"]
        quantity = item.get("quantity", 1)
        acquired = item.get("acquired", "false")

        if (
            item_id not in self.add_set
            or self.add_set[item_id]["timestamp"] < time.time()
        ):
            self.add_set[item_id] = {
                "timestamp": time.time(),
                "quantity": quantity,
                "acquired": acquired,
            }
        else:
            self.add_set[item_id]["quantity"] += quantity
            self.add_set[item_id]["acquired"] = acquired

    def lookup(self, element):
        if element not in self.add_set:
            return False

        if element not in self.remove_set:
            return True

        if self.remove_set[element]["timestamp"] < self.add_set[element]["timestamp"]:
            return True

        return False

    def remove(self, item_id):
        current_time = time.time()
        while True:
            try:
                if item_id in self.add_set and (
                    item_id not in self.remove_set
                    or self.remove_set[item_id]["timestamp"] < current_time
                ):
                    self.remove_set[item_id] = {
                        "timestamp": self.add_set[item_id]["timestamp"],
                        "quantity": self.add_set[item_id]["quantity"],
                        "acquired": self.add_set[item_id]["acquired"],
                    }
                    break
                else:
                    raise TypeError("\nItem not in list")
            except TypeError as error:
                print(str(error))
                item_id = input("Please enter a valid item_id: ")

    def acquire(self, item_id):
        current_time = time.time()
        while True:
            try:
                if item_id in self.add_set and (
                    item_id not in self.remove_set
                    or self.remove_set[item_id]["timestamp"] < current_time
                ):
                    if self.add_set[item_id]["quantity"] == "1":
                        self.add_set[item_id]["quantity"] = "0"
                        self.add_set[item_id]["acquired"] = "true"
                        self.add_set[item_id]["timestamp"] = time.time()

                    elif self.add_set[item_id]["quantity"] == "0":
                        raise TypeError("\nItem already acquired")
                    else:
                        self.add_set[item_id]["quantity"] = str(
                            int(self.add_set[item_id]["quantity"]) - 1
                        )
                        self.add_set[item_id]["timestamp"] = time.time()

                    break
                else:
                    raise TypeError("\nItem not in list")
            except TypeError as error:
                print(str(error))
                item_id = input("Please enter a valid item_id: ")

    def compare(self, other):
        add_subset = set(self.add_set.keys()).issubset(other.add_set.keys())

        remove_subset = set(self.remove_set.keys()).issubset(other.remove_set.keys())

        return add_subset and remove_subset

    def merge(self, other):
        merged_list = ShoppingList()

        for element, details in self.add_set.items():
            if element in other.add_set:
                if details["timestamp"] > other.add_set[element]["timestamp"]:
                    merged_list.add_set[element] = details
                    merged_list.add_set[element]["timestamp"] = time.time()
                else:
                    merged_list.add_set[element] = other.add_set[element]
                    merged_list.add_set[element]["timestamp"] = time.time()

            else:
                merged_list.add_set[element] = details
                merged_list.add_set[element]["timestamp"] = time.time()

        for element, details in other.add_set.items():
            if element not in merged_list.add_set:
                merged_list.add_set[element] = details
                merged_list.add_set[element]["timestamp"] = time.time()

        for element, details in self.remove_set.items():
            if element in other.remove_set:
                if details["timestamp"] > other.remove_set[element]["timestamp"]:
                    merged_list.remove_set[element] = details
                    merged_list.remove_set[element]["timestamp"] = time.time()

                else:
                    merged_list.remove_set[element] = other.remove_set[element]
                    merged_list.remove_set[element]["timestamp"] = time.time()

            else:
                merged_list.remove_set[element] = details
                merged_list.remove_set[element]["timestamp"] = time.time()

        for element, details in other.remove_set.items():
            if element not in merged_list.remove_set:
                merged_list.remove_set[element] = details
                merged_list.remove_set[element]["timestamp"] = time.time()

        return merged_list

    def get_full_list(self):
        full_list = []
        for item_id in self.add_set.keys():
            print("ITem_id", item_id)
            print("LOOKUP", self.lookup(item_id))
            if self.lookup(item_id):
                item_details = self.add_set[item_id]
                full_list.append(
                    {
                        "id": item_id,
                        "acquired": item_details["acquired"],
                        "quantity": item_details["quantity"],
                    }
                )
        return full_list

    def print_list(self):
        print("\nYour list:\n")
        for item in self.get_full_list():
            print("ITEM", item)

    def convert_to_json_format(self):
        list_items = []

        for item in self.get_full_list():
            list_item = {
                "id": item["id"],
                "acquired": item["acquired"],
                "quantity": item["quantity"],
            }
            list_items.append(list_item)

        list_json = {"version": "1.0", "list": list_items}

        return json.dumps(list_json, indent=4)

    def save_list_client_to_file(self, id_list, id_client, hasName=True):
        json_data = self.convert_to_json_format()

        current_directory = os.path.dirname(__file__)

        up_directory = os.path.dirname(current_directory)
        root_directory = os.path.dirname(up_directory)

        if hasName == False:
            filename = os.path.join(
                root_directory, f"storage/client_{id_client}/list_{self.uuid}.json"
            )
        else:
            filename = os.path.join(
                root_directory, f"storage/client_{id_client}/list_{id_list}.json"
            )

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as file:
            file.write(json_data)
        print(f"\nList saved as {filename}")

    def load_list_client_from_file(self, id_client, filename):
        current_directory = os.path.dirname(__file__)

        up_directory = os.path.dirname(current_directory)
        root_directory = os.path.dirname(up_directory)
        filename = os.path.join(
            root_directory, f"storage/client_{id_client}/{filename}"
        )
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                json_data = json.load(file)
                for item in json_data["list"]:
                    self.add(item)
                print(f"List loaded from {filename}")
            return True
        else:
            print("File not found")
            return False

    def load_list_server_from_file(self, filepath):
        try:
            with open(filepath, "r") as file:
                json_data = json.load(file)
                for item in json_data["list"]:
                    self.add(item)
                print(f"List loaded from {filepath}")
        except:
            print("File not found")
            return None
