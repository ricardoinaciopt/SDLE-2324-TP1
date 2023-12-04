import zmq
import uuid
import time
from hash_ring.hash_ring import HashRing
import pickle
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from list_writer.LWW.lww import ShoppingList


class Proxy:
    def __init__(
        self,
        frontend_port_s,
        frontend_port_r,
        backend_port_reach,
        backend_port_online,
        backend_port_r,
        backend_port_s,
        backend_port_hello,
        backend_port_ack,
    ):
        self.context = zmq.Context()

        self.frontend_s = self.context.socket(zmq.PUB)
        self.frontend_r = self.context.socket(zmq.ROUTER)
        self.frontend_s.bind(f"tcp://*:{frontend_port_s}")
        self.frontend_r.bind(f"tcp://*:{frontend_port_r}")

        self.servers = []
        self.serverQueue = []

        self.backend_reach = self.context.socket(zmq.PUB)
        self.backend_reach.bind(f"tcp://*:{backend_port_reach}")
        self.backend_reach.setsockopt(zmq.SNDTIMEO, 1000)
        self.backend_online = self.context.socket(zmq.ROUTER)
        self.backend_online.bind(f"tcp://*:{backend_port_online}")
        self.backend_online.setsockopt(zmq.RCVTIMEO, 1000)

        self.backend_s = self.context.socket(zmq.PUB)
        self.backend_s.setsockopt(zmq.SNDTIMEO, 1000)
        self.backend_s.bind(f"tcp://*:{backend_port_s}")
        self.backend_r = self.context.socket(zmq.ROUTER)
        self.backend_r.setsockopt(zmq.RCVTIMEO, 1000)
        self.backend_r.bind(f"tcp://*:{backend_port_r}")
        self.backend_ack = self.context.socket(zmq.PUB)
        self.backend_ack.bind(f"tcp://*:{backend_port_ack}")
        self.backend_hello = self.context.socket(zmq.ROUTER)
        self.backend_hello.setsockopt(zmq.RCVTIMEO, 1000)
        self.backend_hello.bind(f"tcp://*:{backend_port_hello}")

        self.poller = zmq.Poller()
        self.hash_ring = HashRing()

    def add_server(self, server_id):
        if server_id not in self.servers:
            self.servers.append(server_id)
            self.serverQueue.append(server_id)

            print(f"P> SERVER QUEUE LENGHT: {len(self.serverQueue)}")

            if len(self.serverQueue) == 5:
                self.hash_ring.generate_ring(self.serverQueue)
                self.hash_ring.print_key_ranges(index=True)
                self.serverQueue.clear()

    def remove_server(self, server_id):
        if server_id in self.servers:
            self.servers.remove(server_id)
            self.hash_ring.remove_node(server_id)

    def select_responsible_node(self, key):
        print(f"P> NODE ({self.hash_ring.lookup_node(key)}) SELECTED")
        return self.hash_ring.lookup_node(key)

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
                            try:
                                self.backend_ack.send_multipart(
                                    [server_id.encode(), b"ACK"]
                                )

                                print("P> SENT ACK")
                            except zmq.error.Again as e:
                                print(f"\nC> COULDN'T REACH SERVER: {e}")
                                self.remove_server(server_id)

                if self.backend_r in sockets and self.backend_r.poll(0):
                    message = self.backend_r.recv_multipart()

                    client_id = message[1]
                    list_id = message[3]

                    self.frontend_s.send_multipart([client_id, message[2], list_id])

                if self.frontend_r in sockets and self.frontend_r.poll(0):
                    message = self.frontend_r.recv_multipart()
                    client_id = message[1].decode()
                    list_id = message[3].decode()
                    print("P> C:", list_id)

                    destination_node = self.hash_ring.lookup_node(list_id)
                    if destination_node:
                        # REACH DESTINATION
                        try:
                            print(
                                "\nP> SENDING S_REACH: ",
                                destination_node,
                            )
                            self.backend_reach.send_multipart(
                                [
                                    destination_node.encode(),
                                    b"S_REACH",
                                ]
                            )

                            s_online = self.backend_online.recv_multipart()

                            if s_online[2] == b"S_ONLINE":
                                print("\nP> S_ONLINE RECEIVED")

                        except zmq.error.ZMQError as e:
                            print(f"\nC> COULDN'T REACH SERVER: {e}")
                            self.remove_server(server_uuid)

                        # SEND TO DESTINATION
                        server_uuid = destination_node
                        try:
                            self.backend_s.send_multipart(
                                [
                                    server_uuid.encode(),
                                    message[2],
                                    client_id.encode(),
                                    list_id.encode(),
                                ]
                            )

                            print("\nP> Sending to primary: ", server_uuid)
                        except zmq.error.ZMQError as e:
                            print(f"\nC> COULDN'T REACH SERVER: {e}")
                            self.remove_server(server_uuid)
                        # IF IT'S NOT A GET
                        if message[2] != b"GET_LIST":
                            replica_nodes = self.hash_ring.get_replica_nodes(list_id)

                            if replica_nodes:
                                print(
                                    "\nP> Sending to replicas:",
                                    replica_nodes,
                                )

                                for replica_node in replica_nodes:
                                    self.backend_s.send_multipart(
                                        [
                                            replica_node.encode(),
                                            message[2],
                                            client_id.encode(),
                                            list_id.encode(),
                                        ]
                                    )

                    else:
                        print("NO SERVERS AVAILABLE")

        except zmq.error.ContextTerminated:
            pass
        finally:
            self.frontend_r.close()
            self.frontend_s.close()
            self.backend_r.close()
            self.backend_reach.close()
            self.backend_online.close()
            self.backend_s.close()
            self.backend_ack.close()
            self.backend_hello.close()
            self.context.term()


if __name__ == "__main__":
    proxy = Proxy(
        frontend_port_s=5555,
        frontend_port_r=5556,
        backend_port_reach=5545,
        backend_port_online=5546,
        backend_port_s=5565,
        backend_port_r=5566,
        backend_port_ack=5575,
        backend_port_hello=5576,
    )
    proxy.run()
