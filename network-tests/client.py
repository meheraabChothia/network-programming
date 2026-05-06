import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 8000))

name = input("Name: ")
client.send(name.encode())


def recv_loop():
    while (True):
        response = client.recv(999_999).decode()
        print(f"Sender: {response}\nYou: ", end='')


def send_loop():
    while (True):
        message = input("You: ")
        client.send(message.encode())


t = threading.Thread(target=recv_loop)
t.start()

send_loop()
