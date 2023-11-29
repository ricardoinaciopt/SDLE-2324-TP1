import sys
import os
from list_writer.LWW.lww import ShoppingList
import shutil


class UI:
    def __init__(self, client_id):
        self.client_id = client_id
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            self.process_choice(choice)
            if choice == "0":
                break

    def display_menu(self):
        print("Menu:")
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
            shopping_list.save_list_client_to_file("",self.client_id, False)
            print("List created:", shopping_list.uuid)
            print("\n")
            item_id = input("Insert the item id:")
            item_acquired = 'false'
            item_quantity = input("Insert the item quantity:")
            item = {}
            item['id'] = item_id
            item['acquired'] = item_acquired
            item['quantity'] = item_quantity
            shopping_list.add(item)
            shopping_list.print_list()
            print(shopping_list.uuid)
            shopping_list.save_list_client_to_file(str(shopping_list.uuid), self.client_id, True)
            print("\n")
        elif choice == "2":
            list_id = input("Insert the list id:")
            if(self.get_list_not_created(self.client_id,list_id)):
                filename = "list_" + list_id + ".json"
                shopping_list = ShoppingList()
                shopping_list.load_list_client_from_file(self.client_id,filename)
                shopping_list.print_list()
                print("\n")
        elif choice == "3":
            list_id = input("Insert the list id:")
            if(self.get_list_not_created(self.client_id,list_id)):
                filename = "list_" + list_id + ".json"
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
                shopping_list.load_list_client_from_file(self.client_id,filename)
                # TODO: get from server if online
                shopping_list.load_list_client_from_file(self.client_id,filename)
                shopping_list.add(item)
                shopping_list.merge(shopping_list_old)
                shopping_list.print_list()
                shopping_list.save_list_client_to_file(list_id, self.client_id, True)
                print("\n")
        elif choice == "4":
            list_id = input("Insert the list id:")
            if(self.get_list_not_created(self.client_id,list_id)):
                filename = "list_" + list_id + ".json"
                item_id = input("Insert the item id:")
                shopping_list = ShoppingList()
                print("shopping_list", shopping_list.uuid)
                shopping_list_old = ShoppingList()
                shopping_list.load_list_client_from_file(self.client_id,filename)
                shopping_list.load_list_client_from_file(self.client_id,filename)
                shopping_list.remove(item_id)
                shopping_list.merge(shopping_list_old)
                shopping_list.print_list()
                shopping_list.save_list_client_to_file(list_id, self.client_id, True)
                print("\n")
        elif choice == "5":
            list_id = input("Insert the list id:")
            if (self.get_list_not_created(self.client_id,list_id)):
                filename = "list_" + list_id + ".json"
                item_id = input("Insert the item id:")
                shopping_list = ShoppingList()
                shopping_list_old = ShoppingList()
                shopping_list.load_list_client_from_file(self.client_id,filename)
                shopping_list_old.load_list_client_from_file(self.client_id,filename)
                shopping_list.acquire(item_id)
                shopping_list.merge(shopping_list_old)
                shopping_list.print_list()
                shopping_list.save_list_client_to_file(list_id, self.client_id, True)
                print("\n")
        elif choice == "0":
            print("Exiting...")
        else:
            print("Invalid choice")
            
    def get_list_not_created(self, client_id, list_id):
        current_directory = os.path.dirname(__file__)
        
        storage_directory = os.path.join(current_directory, 'storage')
        
        for root, dirs, files in os.walk(storage_directory):
            for file in files:
                if file == f"list_{list_id}.json":
                    # Construct the path for the target directory
                    client_dir = os.path.join(storage_directory, f"client_{client_id}")

                    # Check if the directory exists, and create it if it doesn't
                    if not os.path.exists(client_dir):
                        os.makedirs(client_dir)

                    # Construct the full paths for source and destination files
                    source_file = os.path.join(root, file)
                    destination_file = os.path.join(client_dir, file)

                    # Copy the file
                    shutil.copy(source_file, destination_file)
                    print(f"File copied to {destination_file}")
                    
                    return True
        
        print("List does not exist")
        return False        
                    


if __name__ == "__main__":
    ui = UI()
