class AuthenticationFailedException(Exception):
    pass


class DataSizeMismatchException(Exception):
    pass


class MissingUploadChunkException(Exception):
    pass


class InvalidUploadDataException(Exception):
    pass


class NotAuthenticatedException(Exception):
    pass


class UploadAlreadyFinishedException(Exception):
    pass


class UploadAlreadyStartedException(Exception):
    pass


class UnexpectedWebsocketClose(Exception):
    pass
