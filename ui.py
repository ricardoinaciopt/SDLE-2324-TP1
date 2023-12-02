import sys
import os
from list_writer.LWW.lww import ShoppingList
import shutil
import pickle


class UI:
    def __init__(self, client):
        self.client = client
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            self.process_choice(choice)
            if int(choice) == 0:
                break
            input("\n[PRESS ENTER TO CONTINUE]\n")
            if os.name == "nt":
                os.system("cls")
            else:
                os.system("clear")

    def display_menu(self):
        print("Menu:")
        print("1. Create list")
        print("2. Print list")
        print("3. Add item to list")
        print("4. Remove item from list")
        print("5. Acquire item")
        print("6. Get list from server")
        print("0. Exit")

    def get_user_choice(self):
        choice = input("Enter your choice: ")
        return choice

    # MENU OPTIONS
    def process_choice(self, choice):
        menu_options = {
            "1": self.create_shopping_list,
            "2": self.view_shopping_list,
            "3": self.add_item_to_shopping_list,
            "4": self.remove_item_from_shopping_list,
            "5": self.acquire_item_in_shopping_list,
            "6": self.get_list_from_server,
            "0": exit,
        }

        option = menu_options.get(choice, self.invalid_choice)
        option()

    def create_shopping_list(self):
        shopping_list = ShoppingList()
        shopping_list.save_list_client_to_file("", self.client.uuid, False)
        print("List created:", shopping_list.uuid)
        print("\n")
        item_id = self.input_name()
        item_acquired = "false"
        item_quantity = self.input_quantity()
        item = {}
        item["id"] = item_id
        item["acquired"] = item_acquired
        item["quantity"] = str(item_quantity)
        shopping_list.add(item)
        shopping_list.print_list()
        print(shopping_list.uuid)
        shopping_list.save_list_client_to_file(
            str(shopping_list.uuid), self.client.uuid, True
        )
        list_to_send = pickle.dumps(shopping_list)
        self.client.send_data(list_to_send, str(shopping_list.uuid))
        print("\n")

    def view_shopping_list(self):
        list_id = input("Insert the list id:")
        if self.get_list_not_created(self.client.uuid, list_id):
            filename = "list_" + list_id + ".json"
            shopping_list = ShoppingList()
            shopping_list.load_list_client_from_file(self.client.uuid, filename)
            shopping_list.print_list()
            print("\n")

    def add_item_to_shopping_list(self):
        list_id = input("Insert the list id:")
        if self.get_list_not_created(self.client.uuid, list_id):
            filename = "list_" + list_id + ".json"
            item_id = self.input_name()
            item_acquired = "false"
            item_quantity = self.input_quantity()
            item = {}
            item["id"] = item_id
            item["acquired"] = item_acquired
            item["quantity"] = str(item_quantity)
            shopping_list = ShoppingList()
            shopping_list_old = ShoppingList()
            shopping_list.load_list_client_from_file(self.client.uuid, filename)
            shopping_list.load_list_client_from_file(self.client.uuid, filename)
            shopping_list.add(item)
            shopping_list.merge(shopping_list_old)
            shopping_list.print_list()
            shopping_list.save_list_client_to_file(list_id, self.client.uuid, True)
            print("\n")

    def remove_item_from_shopping_list(self):
        list_id = input("Insert the list id:")
        if self.get_list_not_created(self.client.uuid, list_id):
            filename = "list_" + list_id + ".json"
            item_id = self.input_name()
            shopping_list = ShoppingList()
            print("shopping_list", shopping_list.uuid)
            shopping_list_old = ShoppingList()
            shopping_list.load_list_client_from_file(self.client.uuid, filename)
            shopping_list.load_list_client_from_file(self.client.uuid, filename)
            shopping_list.remove(item_id)
            shopping_list.merge(shopping_list_old)
            shopping_list.print_list()
            shopping_list.save_list_client_to_file(list_id, self.client.uuid, True)
            print("\n")

    def acquire_item_in_shopping_list(self):
        list_id = input("Insert the list id:")
        if self.get_list_not_created(self.client.uuid, list_id):
            filename = "list_" + list_id + ".json"
            item_id = self.input_name()
            shopping_list = ShoppingList()
            shopping_list_old = ShoppingList()
            shopping_list.load_list_client_from_file(self.client.uuid, filename)
            shopping_list_old.load_list_client_from_file(self.client.uuid, filename)
            shopping_list.acquire(item_id)
            shopping_list.merge(shopping_list_old)
            shopping_list.print_list()
            shopping_list.save_list_client_to_file(list_id, self.client.uuid, True)
            print("\n")

    def get_list_from_server(self):
        list_id = input("Insert the list id: ")

    def invalid_choice(self):
        print("Invalid choice")

    def get_list_not_created(self, client_id, list_id):
        current_directory = os.path.dirname(__file__)

        storage_directory = os.path.join(current_directory, "storage")

        for root, dirs, files in os.walk(storage_directory):
            for file in files:
                if file == f"list_{list_id}.json" and root != os.path.join(
                    storage_directory, f"client_{client_id}"
                ):
                    print("ROOT:", root)
                    print(
                        "PATH", os.path.join(storage_directory, f"client_{client_id}")
                    )
                    client_dir = os.path.join(storage_directory, f"client_{client_id}")

                    if not os.path.exists(client_dir):
                        os.makedirs(client_dir)

                    source_file = os.path.join(root, file)
                    destination_file = os.path.join(client_dir, file)

                    shutil.copy(source_file, destination_file)
                    print(f"File copied to {destination_file}")

                    return True
                elif file == f"list_{list_id}.json" and root == os.path.join(
                    storage_directory, f"client_{client_id}"
                ):
                    return True

        print("List does not exist")
        return False

    def input_name(self):
        while True:
            try:
                item_name = input("Insert the item name:")
                if item_name == "" or item_name == "\n":
                    raise ValueError("Please enter a name.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

        return item_name

    def input_quantity(self):
        while True:
            try:
                item_quantity = int(input("Insert the item quantity:"))
                break
            except ValueError:
                print("Invalid input. Please enter an integer.")
        return item_quantity


if __name__ == "__main__":
    ui = UI()
