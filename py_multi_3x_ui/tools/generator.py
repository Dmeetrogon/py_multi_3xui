import random
from string import ascii_letters,digits
class RandomStuffGenerator:
    @staticmethod
    def generate_email(length:int) -> str:
        email  = [random.choice(ascii_letters + digits) for i in range(length)]
        return ''.join(email)