import zmq
import threading

context = zmq.Context()
socket = context.socket(zmq.DEALER)
socket.connect("tcp://localhost:5559")


def reciever():
    while 1:
        message = socket.recv_string()
        print(f"Received: {message}")


if __name__ == "__main__":
    p1 = threading.Thread(target=reciever)
    p1.start()

    while 1:
        print("\n:>")
        msg = input()
        socket.send_string(msg)
