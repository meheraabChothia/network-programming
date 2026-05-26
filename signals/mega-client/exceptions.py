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
