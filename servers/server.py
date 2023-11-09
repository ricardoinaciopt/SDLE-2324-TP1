import zmq
import uuid


class Server:
    def __init__(self, server_id):
        self.context = zmq.Context()
        self.server_id = server_id
        self.server_socket = self.context.socket(zmq.DEALER)
        self.server_socket.connect("tcp://localhost:5556")
        self.server_socket.send_multipart([server_id.encode(), b"Hello from Server!"])

    def handle_requests(self):
        while True:
            frames = self.server_socket.recv_multipart()
            client_id = frames[0].decode()
            message = frames[1].decode()
            print("C>", message)
            response = f"{message.upper()}"
            self.server_socket.send_multipart([server_id.encode(), response.encode()])


if __name__ == "__main__":
    server_id = str(uuid.uuid4())
    server = Server(server_id)
    print(f"--------------------\nSERVER {server_id} STARTED\n--------------------")
    server.handle_requests()
