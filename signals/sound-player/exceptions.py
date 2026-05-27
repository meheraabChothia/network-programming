# Making a global exception for Client connection statuses
class ClientExceptions(Exception):
    pass


class ClientDoesNotExist(ClientExceptions):
    pass


class ClientConnected(ClientExceptions):
    pass


# Making a global exception for Communcation statuses
class CommucationExceptions(Exception):
    pass


class CommucationSuccess(CommucationExceptions):
    pass


class CommucationFailure(CommucationExceptions):
    pass


# Making a global exception for Server Connection statuses
class ServerExceptions(Exception):
    pass


class ServerConnected(ServerExceptions):
    pass
