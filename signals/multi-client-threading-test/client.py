import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8000))
print(client.recv(999_999))

while (True):
    message = input("What do you want to see reversed? ")
    client.send(message.encode())
    response = client.recv(999_999)
    print(response.decode())
