import zmq
import uuid
import time


class Proxy:
    def __init__(
        self,
        frontend_port_s,
        frontend_port_r,
        backend_port_s,
        backend_port_r,
        backend_port_hello,
        backend_port_ack,
    ):
        self.context = zmq.Context()

        self.frontend_s = self.context.socket(zmq.PUB)
        self.frontend_r = self.context.socket(zmq.ROUTER)
        self.frontend_s.bind(f"tcp://*:{frontend_port_s}")
        self.frontend_r.bind(f"tcp://*:{frontend_port_r}")

        # TODO: call the hash ring instance and add all nodes
        self.servers = []
        self.serverQueue = []

        self.backend_s = self.context.socket(zmq.PUB)
        self.backend_r = self.context.socket(zmq.ROUTER)
        self.backend_ack = self.context.socket(zmq.PUB)
        self.backend_hello = self.context.socket(zmq.ROUTER)
        self.backend_s.bind(f"tcp://*:{backend_port_s}")
        self.backend_r.bind(f"tcp://*:{backend_port_r}")
        self.backend_hello.bind(f"tcp://*:{backend_port_hello}")
        self.backend_ack.bind(f"tcp://*:{backend_port_ack}")

        self.poller = zmq.Poller()

    def add_server(self, server_id):
        # TODO: only add to ring, when server queue = 5, and then empty server queue and re calculate ring.
        # if self.serverQueue.lenght == 5:
        #     hashring.addallnodes...
        if server_id not in self.servers:
            self.servers.append(server_id)

    def run(self):
        try:
            self.poller.register(self.frontend_r, zmq.POLLIN)
            self.poller.register(self.backend_r, zmq.POLLIN)
            self.poller.register(self.backend_hello, zmq.POLLIN)

            while True:
                sockets = dict(self.poller.poll())

                if self.backend_hello in sockets and self.backend_hello.poll(0):
                    message = self.backend_hello.recv_multipart()
                    if message and message[1] == b"S_HELLO":
                        server_id = message[2].decode()
                        node_type = message[3].decode()

                        if node_type == "SERVER" and server_id not in self.servers:
                            print(f"P> Added Server: {server_id}")
                            self.add_server(server_id)

                            self.backend_ack.send_multipart(
                                [server_id.encode(), b"ACK"]
                            )

                            print("P> SENT ACK")

                if self.backend_r in sockets and self.backend_r.poll(0):
                    message = self.backend_r.recv_multipart()

                    sub_msg = message[1]
                    server_msg = message[2].decode()
                    s_id = message[3].decode()

                    print(f"P> S({s_id}): {server_msg}")

                    self.frontend_s.send_multipart([sub_msg, server_msg.encode()])

                if self.frontend_r in sockets and self.frontend_r.poll(0):
                    message = self.frontend_r.recv_multipart()
                    client_id = message[1].decode()
                    msg_data = message[2].decode()
                    print("P> C:", msg_data)
                    if self.servers:
                        # TODO: Instead of selecting node at position 0, call a hashring function to select the responsible node
                        server_uuid = self.servers[0]
                        print("P> Sending to ", server_uuid)
                        self.backend_s.send_multipart(
                            [server_uuid.encode(), msg_data.encode()]
                        )
                    else:
                        print("NO SERVERS AVAILABLE")

        except zmq.error.ContextTerminated:
            pass
        finally:
            self.frontend_r.close()
            self.frontend_s.close()
            self.backend_r.close()
            self.backend_s.close()
            self.backend_ack.close()
            self.backend_hello.close()
            self.context.term()


if __name__ == "__main__":
    proxy = Proxy(
        frontend_port_s=5555,
        frontend_port_r=5556,
        backend_port_s=5565,
        backend_port_r=5566,
        backend_port_ack=5575,
        backend_port_hello=5576,
    )
    proxy.run()
