import zmq
import uuid
import time


class Client:
    def __init__(self, node_type, proxy_address_s, proxy_address_r):
        self.context = zmq.Context()
        self.socket_s = self.context.socket(zmq.XREQ)
        self.socket_r = self.context.socket(zmq.XREQ)
        self.uuid = str(uuid.uuid4())
        self.node_type = node_type
        self.proxy_address_s = proxy_address_s
        self.proxy_address_r = proxy_address_r

        print("CLIENT STARTED: ", self.uuid, "\n--------\n")

    def connect(self):
        self.socket_r.connect(self.proxy_address_r)
        self.socket_s.connect(self.proxy_address_s)

    def send_data(self, message):
        self.socket_s.send_multipart([self.uuid.encode(), message.encode()])
        response = self.socket_r.recv_multipart()
        print(f"Client received response: {response[1].decode()}")

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
            client.send_data("Hello from Client")

            time.sleep(1)

    finally:
        client.close()