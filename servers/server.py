import zmq
import uuid
import time
import pickle
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from list_writer.LWW.lww import ShoppingList


class Server:
    def __init__(
        self,
        node_type,
        proxy_address_s,
        proxy_address_r,
        proxy_address_ack,
        proxy_address_hello,
    ):
        self.context = zmq.Context()
        self.socket_s = self.context.socket(zmq.DEALER)
        self.socket_r = self.context.socket(zmq.SUB)
        self.socket_ack = self.context.socket(zmq.SUB)
        self.socket_hello = self.context.socket(zmq.DEALER)
        self.uuid = str(uuid.uuid4())
        self.node_type = node_type
        self.isAssigned = False
        self.proxy_address_s = proxy_address_s
        self.proxy_address_r = proxy_address_r
        self.proxy_address_ack = proxy_address_ack
        self.proxy_address_hello = proxy_address_hello

        print("\n--------\nS> STARTED:", self.uuid)

    def connect(self):
        self.socket_r.connect(self.proxy_address_r)
        self.socket_r.setsockopt_string(zmq.SUBSCRIBE, self.uuid)
        self.socket_ack.connect(self.proxy_address_ack)
        self.socket_ack.setsockopt_string(zmq.SUBSCRIBE, self.uuid)
        self.socket_hello.connect(self.proxy_address_hello)
        self.socket_s.connect(self.proxy_address_s)
        self.send_hello_request()

    def send_hello_request(self):
        self.socket_hello.send_multipart(
            [b"S_HELLO", self.uuid.encode(), self.node_type.encode()]
        )
        print("S> S_HELLO")

        response = self.socket_ack.recv_multipart()

        s_id = response[0].decode()
        ack = response[1].decode()

        if ack == "ACK":
            print(f"S> RECEIVED {ack} ({s_id})")
        else:
            return

        self.isAssigned = True
        return

    def start_listening(self):
        self.connect()
        while True:
            if self.isAssigned == False:
                self.send_hello_request()

            response = self.socket_r.recv_multipart()

            # check if its a get request

            client_id = response[2]
            list_id = response[3].decode()
            print("RESP:", response[1])
            if list_id != "ACK":
                if response[1] == b'GET_LIST':
                    # TODO: Casll function to get list with specidied ID
                    filename = self.get_list_from_storage(list_id)
                    if (filename != None):
                        shopping_list_to_send = ShoppingList()
                        shopping_list_to_send.load_list_server_from_file(filename)
                        shopping_list_to_send_coded = pickle.dumps(shopping_list_to_send)
                        self.socket_s.send_multipart(
                            [client_id, shopping_list_to_send_coded, list_id.encode(),self.uuid.encode()]
                        )
                    else:
                        self.socket_s.send_multipart([client_id, b"", b"NOT FOUND", self.uuid.encode()])    
                else:
                    list = pickle.loads(response[1])
                    print(f"S> C: {list_id}")
                    print(f"S> C: {list}")
                    # print(self.convert_to_json_format(list.__dict__))

                    self.save_list_server_to_file(list_id, list.__dict__)
                    message = "SAVED IN SERVER"
                    self.socket_s.send_multipart(
                        [client_id, message.encode(), self.uuid.encode()]
                    )
                    print(f"S> SENT {message}")
            else:
                self.socket_s.send_multipart([b"", b"", b""])

    def close(self):
        self.socket_r.close()
        self.socket_ack.close()
        self.socket_hello.close()
        self.socket_s.close()
        self.context.term()

    def convert_to_json_format(self, server_list):
        list_items = []

        for item_id, item_details in server_list["add_set"].items():
            acquired = item_details["acquired"]
            quantity = item_details["quantity"]

            list_item = {
                "id": item_id,
                "acquired": acquired,
                "quantity": quantity,
            }
            list_items.append(list_item)

        list_json = {"version": "1.0", "list": list_items}

        return json.dumps(list_json, indent=4)

    def save_list_server_to_file(self, id_list, list):
        json_data = self.convert_to_json_format(list)

        current_directory = os.path.dirname(__file__)

        root_directory = os.path.dirname(current_directory)

        filename = os.path.join(
            root_directory, f"storage/server_{self.uuid}/list_{id_list}.json"
        )

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as file:
            file.write(json_data)
        print(f"\nList saved as {filename}")
      
    def get_list_from_storage(self, list_id):
        current_directory = os.path.dirname(__file__)
        
        up_directory = os.path.dirname(current_directory)
        
        storage_directory = os.path.join(up_directory, "storage")
        for root, dirs, files in os.walk(storage_directory):
            for file in files:
                if file == f"list_{list_id}.json" and root == os.path.join(storage_directory, f"server_{self.uuid}"):
                    filename = os.path.join(root, file)
                    return filename
        return None        
                    



if __name__ == "__main__":
    server = Server(
        node_type="SERVER",
        proxy_address_r="tcp://localhost:5565",
        proxy_address_s="tcp://localhost:5566",
        proxy_address_ack="tcp://localhost:5575",
        proxy_address_hello="tcp://localhost:5576",
    )

    try:
        server.start_listening()

    finally:
        server.close()
