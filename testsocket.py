import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Binding to localhost at port 8000
server.bind(('localhost', 8000))
server.listen()

(client_socket, address) = server.accept()
print("Connection established.")
client_socket.send(b'Connected to the server, what do you want to say?')

while (True):
    response = client_socket.recv(999_999)
    print(f"Client: {response.decode()}")
    message = input("Server: ")
    client_socket.send(message.encode())
