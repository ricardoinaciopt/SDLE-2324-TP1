import sys
import os
from list_writer.LWW.lww import ShoppingList
from clients.client import Client


class UI:
    def __init__(self):
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            self.process_choice(choice)
            if choice == "0":
                break

    def display_menu(self):
        print("Menu:")
        # TODO: call add item to list after creation
        print("1. Create list")
        print("2. Print list")
        print("3. Add item to list")
        print("4. Remove item from list")
        print("5. Acquire item")
        print("0. Exit")

    def get_user_choice(self):
        choice = input("Enter your choice: ")
        return choice

    def process_choice(self, choice):
        if choice == "1":
            shopping_list = ShoppingList()
            shopping_list.save_list_to_file("", False)
            print("List created:", shopping_list.uuid)
            print("\n")
        elif choice == "2":
            list_id = input("Insert the list id:")
            for filename in os.listdir("lists"):
                if filename == "list_" + list_id + ".json":
                    shopping_list = ShoppingList()
                    shopping_list.load_list_from_file(filename)
                    shopping_list.print_list()
                    print("\n")
        elif choice == "3":
            list_id = input("Insert the list id:")
            for filename in os.listdir("lists"):
                if filename == "list_" + list_id + ".json":
                    item_id = input("Insert the item id:")
                    item_acquired = "false"
                    item_quantity = input("Insert the item quantity:")
                    item = {}
                    item["id"] = item_id
                    item["acquired"] = item_acquired
                    item["quantity"] = item_quantity
                    # from file
                    shopping_list = ShoppingList()
                    shopping_list_old = ShoppingList()
                    shopping_list.load_list_from_file(filename)
                    # TODO: get from server if online
                    shopping_list_old.load_list_from_file(filename)
                    shopping_list.add(item)
                    shopping_list.merge(shopping_list_old)
                    shopping_list.print_list()
                    shopping_list.save_list_to_file(list_id, True)
                    print("\n")
        elif choice == "4":
            list_id = input("Insert the list id:")
            for filename in os.listdir("lists"):
                if filename == "list_" + list_id + ".json":
                    item_id = input("Insert the item id:")
                    shopping_list = ShoppingList()
                    print("shopping_list", shopping_list.uuid)
                    shopping_list_old = ShoppingList()
                    shopping_list.load_list_from_file(filename)
                    shopping_list_old.load_list_from_file(filename)
                    shopping_list.remove(item_id)
                    shopping_list.merge(shopping_list_old)
                    shopping_list.print_list()
                    shopping_list.save_list_to_file(list_id, True)
                    print("\n")
        elif choice == "5":
            list_id = input("Insert the list id:")
            for filename in os.listdir("lists"):
                if filename == "list_" + list_id + ".json":
                    item_id = input("Insert the item id:")
                    shopping_list = ShoppingList()
                    shopping_list_old = ShoppingList()
                    shopping_list.load_list_from_file(filename)
                    shopping_list_old.load_list_from_file(filename)
                    shopping_list.acquire(item_id)
                    shopping_list.merge(shopping_list_old)
                    shopping_list.print_list()
                    shopping_list.save_list_to_file(list_id, True)
                    print("\n")
        elif choice == "0":
            print("Exiting...")
        else:
            print("Invalid choice")


if __name__ == "__main__":
    ui = UI()
