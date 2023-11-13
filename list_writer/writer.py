import os
import json
import time
import uuid
import os.path

directory = "./lists/"


def create_list_item():
    id = input("Enter item ID: ")
    quantity = 0
    try:
        quantity = int(input("Enter item quantity: "))
    except ValueError:
        print("Invalid quantity. Please enter a valid integer.")

    list_item = {"id": id, "acquired": "false", "quantity": quantity}

    return list_item


def write_to_file(data):
    version = 0
    list_data = json.dumps(data)
    new_data = {"version": version, "list": [data]}
    myuuid = uuid.uuid4()
    list_name = "list_" + str(myuuid) + ".json"

    if not os.path.isdir(directory):
        os.mkdir(directory)

    file_path = os.path.join(directory, list_name)
    with open(file_path, "w") as json_file:
        json.dump(new_data, json_file, indent=2)
    return list_name


def append_to_file(list_URL, new_data):
    list_name = list_URL + ".json"
    file_path = os.path.join(directory, list_name)
    try:
        with open(file_path, "r") as temp:
            existing_data = json.load(temp)
    except FileNotFoundError:
        existing_data = []

    full_list = existing_data
    full_list["version"] = int(full_list["version"]) + 1
    full_list["list"].append(new_data)

    file_path = os.path.join(directory, list_name)
    with open(file_path, "w") as temp:
        json.dump(full_list, temp, indent=2)

    return list_name


def verify_file(file_path):
    print(file_path)
    directory = "./lists/"
    base_name = os.path.basename(file_path)
    new_file_path = os.path.join(directory, f"{base_name}.json")
    print(new_file_path)
    return os.path.exists(new_file_path)
    

def main():
    list_name = ""
    os.system("cls")
    print("\nMENU")
    print("\n______________")
    print("\n1 - New List")
    print("\n2 - Edit List")
    op = input("\nInsert option: ")
    if int(op) == 1:
        data = create_list_item()
        list_name = write_to_file(data)
        print(f"\nCreated list with URL: {list_name[:-5]}\nPress ENTER to continue...")
    else:
            old_list = input("\nInsert list URL:")
            if verify_file(old_list):
                data = create_list_item()
                list_name = append_to_file(old_list, data)
                print(f"\nUpdated list with URL: {list_name[:-5]}\nPress ENTER to continue...")
            else:
                print(f"oh no")

    input()
    main()


if __name__ == "__main__":
    main()
