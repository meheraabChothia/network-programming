import socket
import json
from custom_socket import CustomSocket
from utils import COMMANDS, HELP_MSG
import exceptions


HOST = '127.0.0.1'
PORT = 8000


class Client:
    def __init__(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((HOST, PORT))
            self.cust_socket = CustomSocket(self.client)
            server_status = self.cust_socket.cust_recv().decode()
            server_status = getattr(exceptions, server_status)
            self.name = input("What's your name: ")
            self.cust_socket.cust_send(self.name.encode())
            raise server_status
        except exceptions.ServerConnected:
            print("Successfully connected to the server.")
        except ConnectionRefusedError:
            print("Could not connect to the server, check the IP and the port.")

    def display_client_list(self):
        """
        Will just print the list of connected clients.
        The list will be taken from the server in real time.
        """
        client_list = self.cust_socket.cust_recv().decode()
        client_list = json.loads(client_list)

        for i in range(len(client_list)):
            print(f"{i+1}. {client_list[i]}")

    def print_help(self):
        """
        Will print the help messages for each command.
        """
        for i in HELP_MSG:
            print(i)

    def choose_client(self):
        """
        Function to choose a client from the ones in the list
        """
        # Taking the name of the client from the user.
        name = input("Name of the client: ")

        try:
            # Send the name to the server
            self.cust_socket.cust_send(name.encode())

            # Accept the status to see if the client was found
            status = self.cust_socket.cust_recv().decode()
            status = getattr(exceptions, status)
            raise status
        # Handle the status
        except exceptions.ClientDoesNotExist:
            print("Could not find a client with that name.")
            return
        except exceptions.ClientConnected:
            print(f"Connected to the client with the name: {name}")

        try:
            # Take the status of the communication from the server
            communication_status = self.cust_socket.cust_recv().decode()
            communication_status = getattr(exceptions, communication_status)
            raise communication_status
        except exceptions.CommucationFailure:
            print("Communication Failed.")
        except exceptions.CommucationSuccess:
            print("Communcation with the client was successful.")

    def command_manager(self, choice):
        """
        Manages the choice and sends the relevant messages.
        """
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

    def admin_loop(self):
        """
        Manage the admin control flow.
        Take the user's choice and send it off to another function to Manage
            the choice
        """
        # Message to confirm an admin connection to the server.
        print(self.cust_socket.cust_recv().decode())
        while (True):
            choice = input("(/help for help) command: ")
            self.command_manager(choice)

    def client_loop_for_reverse(self):
        """
        Client flow for getting some stirng reversed from the server.
        """
        while (True):
            message = input("What do you want to see reversed? ")
            self.cust_socket.cust_send(message.encode())
            response = self.cust_socket.cust_recv()
            print(response.decode())

    def client_loop(self):
        """
        The current client flow
        where the client communicates with the admin client.
        """
        while (True):
            print("Waiting for communication from the admin:")
            message = self.cust_socket.cust_recv().decode()
            print(f"Message from admin: {message}")

    def control_flow(self):
        """
        The overall control flow for the client file.
        This will decide which client functions to call.
        """
        if self.name == 'admin':
            self.admin_loop()
        else:
            self.client_loop()


if __name__ == "__main__":
    client = Client()
    client.control_flow()
