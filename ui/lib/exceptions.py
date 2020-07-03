class RequestException(Exception):
    def __init__(self, title, message=None, error_code=400):
        self.title = title
        self.message = message if message else title
        self.error_code = error_code


class DomainExists(RequestException):
    pass


class ClientError(RequestException):
    pass


class ServerError(RequestException):
    pass


class DomainNotFound(RequestException):
    pass
