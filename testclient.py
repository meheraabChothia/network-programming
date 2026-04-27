import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(('localhost', 8000))
print(client.recv(999_999))

while (True):
    message = input("Client: ")
    client.send(message.encode())
    response = client.recv(999_999)
    print(f"Server: {response.decode()}")
