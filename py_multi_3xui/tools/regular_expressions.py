import re
class RegularExpressions:
    @staticmethod
    def get_host(url: str):
        match = re.search(r"https?://([^:/]+)", url)
        if match:
            host = match.group(1)
            return host
        else:
            raise Exception('Invalid input')



