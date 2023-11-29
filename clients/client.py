import zmq
import uuid
import time
import random


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

    def send_data(self, message):
        # TODO: Instead of sending message.encode(), send list_id.enconde()
        self.socket_s.send_multipart([self.uuid.encode(), message.encode()])
        # DO NOT REMOVE: JUST FOR SUBSCRIBING
        self.socket_r.setsockopt_string(zmq.SUBSCRIBE, self.uuid)
        print("C> SENT: ", message)
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

        while True:
            msg = "list_" + str(random.randint(0, 999999))
            # TODO: send list_id as msg
            client.send_data(msg)

            time.sleep(1)

    finally:
        client.close()
