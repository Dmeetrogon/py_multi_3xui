import logging
logger = logging.getLogger(__name__)

class HostAlreadyExistException(Exception):
    def __init__(self, message):
        logger.debug(self.__name__ + "was called")
        super().__init__(message)
class ClientNotFoundException(Exception):
    def __init__(self, message):
        logger.debug(self.__name__ + "was called")
        super().__init__(message)
class InvalidConfigException(Exception):
    def __init__(self, message):
        logger.debug(self.__name__ + "was called")
        super().__init__(message)