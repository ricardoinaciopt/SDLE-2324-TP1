import zmq
import uuid
import time


class Server:
    def __init__(self, node_type, proxy_address_s, proxy_address_r):
        self.context = zmq.Context()
        self.socket_s = self.context.socket(zmq.DEALER)
        self.socket_r = self.context.socket(zmq.DEALER)
        self.uuid = str(uuid.uuid4())
        self.node_type = node_type
        self.isAssigned = False
        self.proxy_address_s = proxy_address_s
        self.proxy_address_r = proxy_address_r

        print("SERVER STARTED:", self.uuid, "\n--------\n")

    def connect(self):
        self.socket_r.connect(self.proxy_address_r)
        self.socket_s.connect(self.proxy_address_s)
        self.send_hello_request()

    def send_hello_request(self):
        self.socket_s.send_multipart(
            [b"S_HELLO", self.uuid.encode(), self.node_type.encode()]
        )

        response = self.socket_r.recv_multipart()
        ack = response[1].decode()
        print(f"RECEIVED {ack}")
        self.socket_r.send(b"CONNECTED")

        self.isAssigned = True

    def start_listening(self):
        self.connect()
        while True:
            if self.isAssigned == False:
                self.send_hello_request()

            response = self.socket_r.recv_multipart()

            client_message = response[1].decode()

            print(f">: {client_message}")
            msg_to_send = client_message.upper()
            self.socket_s.send(msg_to_send.encode())
            print(f"SENT: {msg_to_send}")

    def close(self):
        self.socket_r.close()
        self.socket_s.close()
        self.context.term()


if __name__ == "__main__":
    server = Server(
        node_type="SERVER",
        proxy_address_r="tcp://localhost:5565",
        proxy_address_s="tcp://localhost:5566",
    )

    try:
        server.start_listening()

    finally:
        server.close()
