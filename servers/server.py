import zmq
import uuid
import time


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
            list_id = response[1].decode()
            client_id = response[2]
            if list_id != "ACK":
                print(f"S> C: {list_id}")
                # TODO: Instead of converting to lowercase, check if it has list, if not save on fodler with name = self.uuid, and then merge the list
                list_to_send = list_id.upper()
                self.socket_s.send_multipart(
                    [client_id, list_to_send.encode(), self.uuid.encode()]
                )
                print(f"S> SENT {list_to_send}")
            else:
                self.socket_s.send_multipart([b"", b"", b""])

    def close(self):
        self.socket_r.close()
        self.socket_ack.close()
        self.socket_hello.close()
        self.socket_s.close()
        self.context.term()


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
