import zmq
import uuid
import time


class Proxy:
    def __init__(
        self, frontend_port_s, frontend_port_r, backend_port_s, backend_port_r
    ):
        self.context = zmq.Context()

        # Frontend sockets (clients connect here)
        self.frontend_s = self.context.socket(zmq.DEALER)
        self.frontend_r = self.context.socket(zmq.ROUTER)
        self.frontend_s.bind(f"tcp://*:{frontend_port_s}")
        self.frontend_r.bind(f"tcp://*:{frontend_port_r}")

        # Backend sockets (servers connect here)
        self.servers = []
        self.backend_s = self.context.socket(zmq.DEALER)
        self.backend_r = self.context.socket(zmq.ROUTER)
        self.backend_s.bind(f"tcp://*:{backend_port_s}")
        self.backend_r.bind(f"tcp://*:{backend_port_r}")

    def add_server(self, server_id):
        if server_id not in self.servers:
            self.servers.append(server_id)

    def handle_hello_request(self):
        hello_message = self.backend_r.recv_multipart()
        if hello_message and hello_message[1] == b"S_HELLO":
            server_id = hello_message[2].decode()
            node_type = hello_message[3].decode()

            if node_type == "SERVER" and server_id not in self.servers:
                print(f"Added Server: {server_id}")
                self.add_server(server_id)

            self.backend_s.send_multipart([server_id.encode(), b"ACK"])

    def run(self):
        try:
            poller = zmq.Poller()
            poller.register(self.frontend_r, zmq.POLLIN)
            poller.register(self.backend_r, zmq.POLLIN)

            while True:
                sockets = dict(poller.poll())

                if self.frontend_r in sockets:
                    message = self.frontend_r.recv_multipart()
                    client_id = message[1].decode()
                    msg_data = message[2].decode()
                    print("CLIENT:", msg_data)
                    if self.servers:
                        server_uuid = self.servers[0]
                        print("Sending to ", server_uuid)
                        self.backend_s.send_multipart(
                            [server_uuid.encode(), msg_data.encode()]
                        )
                    else:
                        print("No servers available to handle the request.")

                if self.backend_r in sockets:
                    # register the server
                    self.handle_hello_request()
                    message = self.backend_r.recv_multipart()
                    print("SERVER: ", message[1].decode())

                    # Route the message back to the client
                    client_uuid = message[0]
                    self.frontend_s.send_multipart([client_uuid, message[1]])

        except zmq.error.ContextTerminated:
            pass
        finally:
            self.frontend_r.close()
            self.frontend_s.close()
            self.backend_r.close()
            self.backend_s.close()
            self.context.term()


if __name__ == "__main__":
    proxy = Proxy(
        frontend_port_s=5555,
        frontend_port_r=5556,
        backend_port_s=5565,
        backend_port_r=5566,
    )
    proxy.run()
