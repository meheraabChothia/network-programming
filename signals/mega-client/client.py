import socket
import json
from custom_socket import CustomSocket
from utils import COMMANDS, HELP_MSG
import exceptions


HOST = '127.0.0.1'
PORT = 8000


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))
        self.cust_socket = CustomSocket(self.client)
        print(self.cust_socket.cust_recv())
        self.name = input("What's your name: ")
        self.cust_socket.cust_send(self.name.encode())

    def client_sorter(self):
        if self.name == 'admin':
            self.admin_loop()
        else:
            self.client_loop()

    def display_client_list(self):
        client_list = self.cust_socket.cust_recv().decode()
        client_list = json.loads(client_list)

        for i in range(len(client_list)):
            print(f"{i+1}. {client_list[i]}")

    def print_help(self):
        for i in HELP_MSG:
            print(i)

    def choose_client(self):
        name = input("name of the client: ")
        self.cust_socket.cust_send(name.encode())
        status = self.cust_socket.cust_recv().decode()
        if (getattr(exceptions, status) == exceptions.ClientConnected):
            print(self.cust_socket.cust_recv())
        elif (getattr(exceptions, status) == exceptions.ClientDoesNotExist):
            print("Could not find that client.")

    def admin_loop(self):
        """
        Loop Flow:
        Option to choose between:
            1. List the clients
            2. Choose a client
        Should have an open input where the user can
            enter '/list' to see the list of clients.
        And enter /choose {client_name} to choose the
            client to send a command to.
        """
    # Message to confirm an admin connection to the server.
        print(self.cust_socket.cust_recv().decode())
        while (True):
            choice = input("(/help for help) command: ")
            if choice == COMMANDS['help']:
                # Printing help messages
                self.print_help()

            elif choice == COMMANDS['list']:
                # Get the list of connected clients.
                self.cust_socket.cust_send(choice.encode())
                self.display_client_list()

            elif choice == COMMANDS['choose']:
                # To send the client name to the server
                self.cust_socket.cust_send(choice.encode())
                self.choose_client()

            else:
                print("Could not find that command.")

    def client_loop_for_reverse(self):
        while (True):
            message = input("What do you want to see reversed? ")
            self.cust_socket.cust_send(message.encode())
            response = self.cust_socket.cust_recv()
            print(response.decode())

    def client_loop(self):
        while (True):
            print("Waiting for communication from the admin:")
            message = self.cust_socket.cust_recv().decode()
            print(f"Message from admin: {message}")

    def control_flow(self):
        if self.name == 'admin':
            self.admin_loop()
        else:
            self.client_loop()


if __name__ == "__main__":
    client = Client()
    client.control_flow()
