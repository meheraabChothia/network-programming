import socket
import threading


class CustomSocket:
    def __init__(self, client):
        self.client = client

    def cust_send(self, message):
        """
        Should add a check to see if the message is encoded.
        If it is leave it as is and if not then encode it.
        """
        return self.client.send(message)

    def cust_recv(self):
        """
        For now every message being received will accept 999,999 bytes.
        """
        return self.client.recv(999_999)


class ClientMaker():
    def __init__(self, server):
        (self.client, self.addr) = server.accept()
        self.client.send(b"Connected to the server.")
        self.name = self.client.recv(999_999).decode()
        self.cs = CustomSocket(self.client)

    def reverse(self):
        while (True):
            print(f"Interacting with client {self.addr}")
            message = self.cs.cust_recv().decode()
            print(f"Received this message: {
                  message}\nFrom client: {self.addr}")
            rev = message[::-1]
            self.cs.cust_send(rev.encode())
            print(f"Sent a reversed message to client {self.addr}")


class ClientController():
    def __init__(self):
        self.clients_dict = {}
        self.threads_dict = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("", 8000))
        self.server.listen()

    def connection_loop(self):
        while (True):
            client = ClientMaker(self.server)
            if client.name.lower() == 'admin':
                # Make a function to do stuff with the mega admin
                # and throw it to a thread.
                megaClient = MegaClientControls(
                    megaClient=client, clientController=self)
                megaThread = threading.Thread(
                    target=megaClient.mega_client_loop)
                megaThread.start()
                print("IN")
                continue

            # Can leave the rest of the code as is.
            # But can make functions to manage this
            self.clients_dict[client.name] = client
            print(
                f"{"="*70}\nConnected to a client with the name: {client.name}\n{"="*70}")

            self.threads_dict[client.name] = threading.Thread(
                target=client.reverse)
            self.threads_dict[client.name].start()
            print("Pushed the client to another thread.")


class MegaClientControls:
    def __init__(self, megaClient: socket.socket,
                 clientController: ClientController):
        self.client = megaClient.client
        print(type(self.client))
        self.controller = clientController
        self.cs = CustomSocket(self.client)

    def choose_client(self):
        self.cs.cust_send(self.controller.clients_dict)
        # Going to leave this like this for now. Need to see what gets printed and what it looks like

    def mega_client_loop(self):
        self.choose_client()


def main():
    controller = ClientController()
    controller.connection_loop()


if __name__ == "__main__":
    main()
