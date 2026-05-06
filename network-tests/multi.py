import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("", 8000))
server.listen()


class custom_socket:
    def __init__(self, server):
        (self.client, self.address) = server.accept()
        self.name = self.client.recv(999_999).decode()  # For debugging
        print(f"We got a client named: {self.name}")

    def transfer(self, recipient):
        while (True):
            message = recipient.client.recv(999_999)
            print(f"Received a message from {self.name}.")
            self.client.send(message)


client1 = custom_socket(server)
client2 = custom_socket(server)

t = threading.Thread(target=client1.transfer, args=(client2,))
t.start()

client2.transfer(client1)
