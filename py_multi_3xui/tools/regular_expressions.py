import re
import logging
logger = logging.getLogger(__name__)
class RegularExpressions:
    @staticmethod
    def get_host(url: str):
        logger.debug(f"get host from {url}")
        match = re.search(r"https?://([^:/]+)", url)
        if match:
            host = match.group(1)
            return host
        else:
            raise Exception('Invalid input')



