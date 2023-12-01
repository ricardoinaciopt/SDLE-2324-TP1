import zmq
import uuid
import time
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui import UI

class Client:
    def __init__(self, node_type, proxy_address_s, proxy_address_r):
        self.context = zmq.Context()
        self.socket_s = self.context.socket(zmq.XREQ)
        self.socket_r = self.context.socket(zmq.SUB)
        self.uuid = str(uuid.uuid4())
        self.node_type = node_type
        self.proxy_address_s = proxy_address_s
        self.proxy_address_r = proxy_address_r

        print("\n--------\nC> STARTED: ", self.uuid)

    def connect(self):
        self.socket_r.connect(self.proxy_address_r)
        self.socket_s.connect(self.proxy_address_s)

    def send_data(self, list, list_id):
        # TODO: Instead of sending message.encode(), send list_id.enconde()
        self.socket_s.send_multipart([self.uuid.encode(), list, list_id.encode()])
        # DO NOT REMOVE: JUST FOR SUBSCRIBING
        self.socket_r.setsockopt_string(zmq.SUBSCRIBE, self.uuid)
        print("C> SENT: ", list)
        print("C> SENT: ", list_id)
        # response from server
        response = self.socket_r.recv_multipart()
        print(f"C> S: {response[1].decode()}")
        # TODO: see better option, or use pickle

    def close(self):
        self.socket_r.close()
        self.socket_s.close()
        self.context.term()   


# Example usage
if __name__ == "__main__":
    client = Client(
        node_type="CLIENT",
        proxy_address_r="tcp://localhost:5555",
        proxy_address_s="tcp://localhost:5556",
    )

    try:
        client.connect()
        print(client.uuid)
        #list_id=input("Give the list id: ")
        #client.send_data(list_id)
        UI(client)

    finally:
        client.close()
