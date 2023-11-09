import zmq
import uuid


class Proxy:
    def __init__(self):
        self.context = zmq.Context()
        self.client_socket = self.context.socket(zmq.DEALER)
        self.client_socket.bind("tcp://*:5555")
        self.server_socket = self.context.socket(zmq.DEALER)
        self.server_socket.bind("tcp://*:5556")
        self.connected_clients = set()
        self.connected_servers = set()

    def start_proxy(self):
        poller = zmq.Poller()
        poller.register(self.client_socket, zmq.POLLIN)
        poller.register(self.server_socket, zmq.POLLIN)

        while True:
            sockets = dict(poller.poll())

            if (
                self.client_socket in sockets
                and sockets[self.client_socket] == zmq.POLLIN
            ):
                frames = self.client_socket.recv_multipart()

                client_id = frames[0].decode()
                message = frames[1].decode()

                print(f"C: {message}")

                if client_id not in self.connected_clients:
                    self.connected_clients.add(client_id)
                    print(f"New client connected: {client_id}")
                    print("Connected Clients:", list(self.connected_clients))

                self.send_to_server(client_id, message)

            if (
                self.server_socket in sockets
                and sockets[self.server_socket] == zmq.POLLIN
            ):
                frames = self.server_socket.recv_multipart()

                server_id = frames[0].decode()
                message = frames[1].decode()
                print("S::", message)
                if server_id not in self.connected_servers:
                    self.connected_servers.add(server_id)
                    print(f"New server connected: {server_id}")
                    print("Connected Servers:", list(self.connected_servers))

                self.client_socket.send_multipart(
                    [server_id.encode(), message.encode()]
                )

    def send_to_server(self, c_id, msg):
        self.server_socket.send_multipart([c_id.encode(), msg.encode()])


if __name__ == "__main__":
    proxy = Proxy()
    proxy.start_proxy()
