import socket
import threading
import json
from custom_socket import CustomSocket
from utils import COMMANDS
import exceptions

HOST = ""
PORT = 8000


class Client:
    """
    Class exclusively used to make client socket objects.
    """

    def __init__(self, server: 'Server'):
        self.server = server
        (self.client, self.addr) = self.server.server.accept()
        self.cust_socket = CustomSocket(self.client)
        self.cust_socket.cust_send(
            exceptions.ServerConnected.__name__.encode())
        self.name = self.client.recv(999_999).decode()

    def get_client_list(self):
        return list(self.server.clients_dict.keys())

    def get_client_list_encoded(self):
        client_list = json.dumps(
            list(
                self.server.clients_dict.keys()
            )).encode()
        return client_list

    def select_client(self):
        name = self.cust_socket.cust_recv().decode()
        if name not in self.get_client_list():
            self.cust_socket.cust_send(
                exceptions.ClientDoesNotExist.__name__.encode())
            return
        else:
            self.connected_client = self.server.clients_dict[name]
            self.cust_socket.cust_send(
                exceptions.ClientConnected.__name__.encode())
            # Need to replace the line below to change what the admin does
            self.do_something()

    def do_something(self):
        if self.connected_client.cust_socket.cust_send(
                b"Message from the Mega Client"):
            self.cust_socket.cust_send(
                exceptions.CommucationSuccess.__name__.encode())
        else:
            self.cust_socket.cust_send(
                exceptions.CommucationFailure.__name__.encode())

    def admin_control_loop(self):
        """
        Should control the entire interaction loop between the server and the mega client.
        Flow should be something like this:
        1. Send a list of connected clients.
            a. Or maybe wait for the client to ask for the list.
                Mainly because we need to write the logic to ask for the list again anyways.
                For now since I am testing this let's just send it firt.
        """
        self.cust_socket.cust_send(b"Connected to the Server as an admin!")
        while (True):
            print("Interacting with the admin client.")
            choice = self.cust_socket.cust_recv().decode()
            if choice == COMMANDS['list']:
                self.cust_socket.cust_send(self.get_client_list_encoded())
            elif choice == COMMANDS['choose']:
                self.select_client()
            else:
                print(f"The dude sent some weird command: {choice}")

    def reverse(self):
        while (True):
            print(f"Interacting with client {self.addr}")
            message = self.cust_socket.cust_recv().decode()
            print(f"Received this message: {
                  message}\nFrom client: {self.addr}")
            rev = message[::-1]
            self.cust_socket.cust_send(rev.encode())
            print(f"Sent a reversed message to client {self.addr}")
            print("="*50)


class Server:
    """
    Anything that the server should control will be here
    """

    def __init__(self):
        self.clients_dict = {}
        self.threads_dict = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen()

    def connection_loop(self):
        while (True):
            client = Client(self)
            self.clients_dict[client.name] = client
            thread = self.client_sorter(client)
            self.threads_dict[client.name] = thread
            thread.start()
            print("Pushed the client to another thread.")

    def client_sorter(self, client: Client) -> threading.Thread:
        """
        Sorts the clients based on their names and returns the relevant thread.
        For now normal clients do not need a new thread so keeping the old code there.

        """
        if client.name == 'admin':
            return self.get_admin_thread(client)
        else:
            # Now that we're letting the clients just wait for the admin to talk to them,
            # we no longer need to run them on a thread. Not for now atleast.
            return threading.Thread(target=client.reverse)

    def get_admin_thread(self, client: Client) -> threading.Thread:
        """
        Should assign the admin thread and send it to the client sorter
        """
        admin_thread = threading.Thread(
            target=client.admin_control_loop)
        return admin_thread


if __name__ == '__main__':
    server = Server()
    server.connection_loop()
