class HostAlreadyExistException(Exception):
    def __init__(self, message):
        super().__init__(message)
class ClientNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)
class InvalidConfigException(Exception):
    def __init__(self, message):
        super().__init__(message)
class ServerNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)