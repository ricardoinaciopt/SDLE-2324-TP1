import zmq
import uuid
import time
import random
import sys
import os
import pickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui import UI


class Client:
    def __init__(self, node_type, proxy_address_s, proxy_address_r):
        self.context = zmq.Context()
        self.socket_s = self.context.socket(zmq.DEALER)
        self.socket_r = self.context.socket(zmq.SUB)
        self.uuid = str(uuid.uuid4())
        self.node_type = node_type
        self.proxy_address_s = proxy_address_s
        self.proxy_address_r = proxy_address_r

        print("\n--------\nC> STARTED: ", self.uuid)

    def connect(self):
        self.socket_r.connect(self.proxy_address_r)
        self.socket_r.setsockopt(zmq.RCVTIMEO, 1000)
        self.socket_r.setsockopt_string(zmq.SUBSCRIBE, self.uuid)
        self.socket_s.connect(self.proxy_address_s)
        self.socket_s.setsockopt(zmq.SNDTIMEO, 1000)

    def send_data(self, list, list_id):
        # try to upload to server

        tries = 0
        while tries != 3:
            tries += 1
            try:
                self.socket_s.send_multipart(
                    [self.uuid.encode(), list, list_id.encode()]
                )
                print("\nC> UPLOADING LIST: ", list_id)
                print(f"\nC> [TRIES: {tries}]")

                merge_msg = self.socket_r.recv_multipart()
                saved_msg = self.socket_r.recv_multipart()
                response = self.socket_r.recv_multipart()
                print(f"\nC> UPLOAD SUCCESSFUL: {response[1].decode()}")
                break
            except zmq.error.Again as e:
                print(f"\nC> COULDN'T UPLOAD: {e}")
        print("C> LIST SAVED LOCALLY")

    def send_get(self, list_id):
        tries = 0
        while tries != 3:
            try:
                tries += 1
                self.socket_s.send_multipart(
                    [self.uuid.encode(), b"GET_LIST", list_id.encode()]
                )

                print("\nC> WAITING FOR LIST...")
                print(f"\nC> [TRIES: {tries}]")

                response = self.socket_r.recv_multipart()

                list_id = response[2].decode()
                if list_id == "NOT FOUND":
                    print("\nC> LIST NOT FOUND")
                elif (response[1] == b"MERGED IN SERVER") or (
                    response[1] == b"SAVED IN SERVER"
                ):
                    print("\nC> NO LIST RECEIVED")

                else:
                    list_from_server = pickle.loads(response[1])
                    list_from_server.save_list_client_to_file(
                        id_list=list_id, id_client=self.uuid
                    )

                    break

            except zmq.error.Again as e:
                print(f"\nC> COULDN'T GET: {e}")

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
        UI(client)
    finally:
        client.close()
        exit()
