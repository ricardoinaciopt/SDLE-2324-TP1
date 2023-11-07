import zmq

context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind("tcp://*:5559")

clients = set()

while True:
    # Receive a message from any client
    client_id = socket.recv()
    message = socket.recv_string()
    clients.add(client_id)

    # Relay the message to the other client(s)
    for client in clients:
        if client != client_id:  # Don't send back to the originating client
            socket.send(client, zmq.SNDMORE)
            socket.send_string(message)
