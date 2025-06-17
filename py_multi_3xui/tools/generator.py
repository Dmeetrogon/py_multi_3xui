import random
from string import ascii_letters,digits

import logging
logger = logging.getLogger(__name__)

class RandomStuffGenerator:
    @staticmethod
    def generate_email(length:int = 10) -> str:
        """
        Generate pseudorandom email. Do not check its availability for current server
        *email in context of 3xui means unique username
        :param length: length of an email
        :return: the email
        """
        logger.debug(f"Generate email length {length}")
        email  = [random.choice(ascii_letters + digits) for i in range(length)]
        return ''.join(email)