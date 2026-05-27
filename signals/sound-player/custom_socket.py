import socket


class CustomSocket:
    """
    Making a custom socket class to wrap socket.send and socket.recv around an abstraction.
    Just in case I need to change it later.
    """

    def __init__(self, client: socket.socket):
        self.client = client

    def cust_send(self, message):
        return self.client.send(message)

    def cust_recv(self):
        message = self.client.recv(999_999)
        if message:
            return message
        else:
            raise RuntimeError("Connection closed")
