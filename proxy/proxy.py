import zmq
import uuid
import time


class Proxy:
    def __init__(
        self, frontend_port_s, frontend_port_r, backend_port_s, backend_port_r
    ):
        self.context = zmq.Context()

        self.frontend_s = self.context.socket(zmq.DEALER)
        self.frontend_r = self.context.socket(zmq.ROUTER)
        self.frontend_s.bind(f"tcp://*:{frontend_port_s}")
        self.frontend_r.bind(f"tcp://*:{frontend_port_r}")

        self.servers = []
        self.backend_s = self.context.socket(zmq.DEALER)
        self.backend_r = self.context.socket(zmq.ROUTER)
        self.backend_s.bind(f"tcp://*:{backend_port_s}")
        self.backend_r.bind(f"tcp://*:{backend_port_r}")

        self.poller = zmq.Poller()

    def add_server(self, server_id):
        if server_id not in self.servers:
            self.servers.append(server_id)

    def handle_hello_request(self):
        message = self.backend_r.recv_multipart()
        if message and message[1] == b"S_HELLO":
            server_id = message[2].decode()
            node_type = message[3].decode()

            if node_type == "SERVER" and server_id not in self.servers:
                print(f"Added Server: {server_id}")
                self.add_server(server_id)

                self.backend_s.send_multipart([server_id.encode(), b"ACK"])
                return True
        else:
            return message

    def run(self):
        try:
            self.poller.register(self.frontend_r, zmq.POLLIN)
            self.poller.register(self.backend_r, zmq.POLLIN)

            while True:
                sockets = dict(self.poller.poll())

                while self.backend_r in sockets and self.backend_r.poll(0):
                    message = self.handle_hello_request()
                    if message == True:
                        break

                    server_msg = message[1].decode()
                    client_uuid = message[0]

                    print("SERVER: ", message[1].decode())
                    print("Sending to ", message[1].decode())
                    self.frontend_s.send_multipart([client_uuid, server_msg.encode()])

                if self.frontend_r in sockets:
                    if self.frontend_r.poll(0):
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
