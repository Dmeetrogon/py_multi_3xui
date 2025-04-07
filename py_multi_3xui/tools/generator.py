import random
from string import ascii_letters,digits

import logging
logger = logging.getLogger(__name__)

class RandomStuffGenerator:
    @staticmethod
    def generate_email(length:int) -> str:
        logger.debug("generate email")
        email  = [random.choice(ascii_letters + digits) for i in range(length)]
        return ''.join(email)
