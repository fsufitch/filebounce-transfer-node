class AuthenticationFailedException(Exception):
    pass


class DataSizeMismatchException(Exception):
    pass


class InvalidUploadDataException(Exception):
    pass


class NotAuthenticatedException(Exception):
    pass


class UploadAlreadyFinishedException(Exception):
    pass


class UploadAlreadyStartedException(Exception):
    pass
