import zmq
import uuid


class Client:
    def __init__(self, client_id):
        self.context = zmq.Context()
        self.client_id = client_id
        self.client_socket = self.context.socket(zmq.DEALER)
        self.client_socket.connect("tcp://localhost:5555")

    def send_request(self, message):
        self.client_socket.send_multipart([client_id.encode(), message.encode()])


if __name__ == "__main__":
    client_id = str(uuid.uuid4())
    client = Client(client_id)
    print(f"--------------------\nCLIENT {client_id} STARTED\n--------------------")
    while True:
        server_id, response = client.client_socket.recv_multipart()
        print(f"S > {response.decode()}")
        message = input(": >")
        if not message:
            break
        client.send_request(message)
