import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", 8000))
server.listen()

# Now we need to make a loop for connecting to clients and spawning different threads


class client_maker():
    def __init__(self, server):
        (self.client, self.addr) = server.accept()
        self.client.send(b"Connected to the server.")
        # print(
        # f"{"="*50}\nConnected to a client with the address: {self.addr}\n{"="*50}")

    def reverse(self):
        while (True):
            print(f"Interacting with client {self.addr}")
            message = self.client.recv(999_999).decode()
            print(f"Received this message: {
                  message}\nFrom client: {self.addr}")
            rev = message[::-1]
            self.client.send(rev.encode())
            print(f"Sent a reversed message to client {self.addr}")


clients_list = []
threads_list = []
index = 0
while (True):
    clients_list.append(client_maker(server))
    print(
        f"{"="*70}\nConnected to a client with the address: {clients_list[index].addr}\n{"="*70}")
    threads_list.append(threading.Thread(target=clients_list[index].reverse))
    threads_list[index].start()
    print("Pushed the client to another thread.")
    index += 1
