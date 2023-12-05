import sys
import os
from list_writer.LWW.lww import ShoppingList
import shutil
import pickle
import re
import time


class UI:
    def __init__(self, client):
        self.client = client
        while True:
            self.program_loop()

    def program_loop(self):
        self.display_menu()
        choice = self.get_user_choice()
        self.process_choice(choice)

        input("\n[PRESS ENTER TO CONTINUE]\n")

    def display_menu(self):
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

        print("Menu:")
        print("1. Create list")
        print("2. Print list")
        print("3. Add item to list")
        print("4. Remove item from list")
        print("5. Acquire item")
        print("6. Get list from server")
        print("7. Save list in server")
        print("8. Delete list")
        print("0. Exit")

    def get_user_choice(self):
        try:
            choice = input("ENTER SELECTION: ")
            if 0 <= int(choice) <= 8 or choice.strip() == "":
                return choice
            else:
                print(f"\n[INVALID SELECTION: {choice}]\n[PRESS ENTER KEY]")
                input()
                self.program_loop()
        except:
            print(f"\n[INVALID SELECTION: {choice}]")
            time.sleep(1.5)
            self.program_loop()

    # MENU OPTIONS
    def process_choice(self, choice):
        menu_options = {
            "1": self.create_shopping_list,
            "2": self.view_shopping_list,
            "3": self.add_item_to_shopping_list,
            "4": self.remove_item_from_shopping_list,
            "5": self.acquire_item_in_shopping_list,
            "6": self.get_list_from_server,
            "7": self.save_list_in_server,
            "8": self.delete_list,
            "0": self.exiting,
        }

        option = menu_options.get(choice, self.invalid_choice)
        option()

    def create_shopping_list(self):
        shopping_list = ShoppingList()
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
        list_id = self.check_list_id()
        filename = "list_" + list_id + ".json"
        shopping_list = ShoppingList()
        list_res = shopping_list.load_list_client_from_file(self.client.uuid, filename)
        if list_res != False:
            shopping_list.print_list()
        print("\n")

    def add_item_to_shopping_list(self):
        list_id = self.check_list_id()
        filename = "list_" + list_id + ".json"
        item_id = self.input_name()
        item_acquired = "false"
        item_quantity = self.input_quantity()
        item = {}
        item["id"] = item_id
        item["acquired"] = item_acquired
        item["quantity"] = str(item_quantity)
        shopping_list = ShoppingList()
        shopping_list.load_list_client_from_file(self.client.uuid, filename)
        shopping_list.add(item)
        shopping_list.print_list()
        shopping_list.save_list_client_to_file(list_id, self.client.uuid, True)
        self.save_list_in_server(shopping_list, list_id)
        print("\n")

    def remove_item_from_shopping_list(self):
        list_id = self.check_list_id()
        filename = "list_" + list_id + ".json"
        item_id = self.input_name()
        shopping_list = ShoppingList()
        print("shopping_list", shopping_list.uuid)
        shopping_list.load_list_client_from_file(self.client.uuid, filename)
        shopping_list.remove(item_id)
        shopping_list.print_list()
        shopping_list.save_list_client_to_file(list_id, self.client.uuid, True)
        print("SL:", shopping_list.__dict__)
        self.save_list_in_server(shopping_list, list_id)
        print("\n")

    def acquire_item_in_shopping_list(self):
        list_id = self.check_list_id()
        filename = "list_" + list_id + ".json"
        item_id = self.input_name()
        shopping_list = ShoppingList()
        shopping_list.load_list_client_from_file(self.client.uuid, filename)
        shopping_list.acquire(item_id)
        shopping_list.print_list()
        shopping_list.save_list_client_to_file(list_id, self.client.uuid, True)
        self.save_list_in_server(shopping_list, list_id)
        print("\n")

    def delete_list(self):
        list_id = self.check_list_id()
        filename = "list_" + list_id + ".json"
        shopping_list = ShoppingList()
        if shopping_list.load_list_client_from_file(self.client.uuid, filename):
            current_directory = os.path.dirname(__file__)
            filename = os.path.join(
                current_directory, "storage", f"client_{self.client.uuid}", filename
            )
            os.remove(filename)
            print("List deleted")

    def get_list_from_server(self):
        list_id = self.check_list_id()
        self.client.send_get(list_id)

    def save_list_in_server(self, shopping_list=None, list_id=None):
        if list_id == None and shopping_list == None:
            list_id = self.check_list_id()
            filename = "list_" + list_id + ".json"

            shopping_list = ShoppingList()
            shopping_list.load_list_client_from_file(self.client.uuid, filename)
        list_to_send = pickle.dumps(shopping_list)
        self.client.send_data(list_to_send, list_id)

    def invalid_choice(self):
        print("INVALID CHOICE")

    def exiting(self):
        print("EXITING...")
        exit()
        return

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
                item_quantity = int(input("Insert the item quantity: "))
                if item_quantity != 0:
                    break
                else:
                    print("Quantity should not be equal to 0. Please try again.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

        return item_quantity

    def check_list_id(self):
        while True:
            try:
                input_id = input("Insert the list id: ")
                if not re.match(
                    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$",
                    input_id,
                ):
                    raise ValueError("Please enter a uuid4 list id.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

        return str(input_id)


if __name__ == "__main__":
    ui = UI()
