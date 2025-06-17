import re
import logging
logger = logging.getLogger(__name__)
class RegularExpressions:
    @staticmethod
    def get_host(url: str):
        """
        Get host from url(with 3xui port and panel_path)
        :param url:
        :return:
        """
        logger.debug(f"Get host from {url}")
        match = re.search(r"https?://([^:/]+)", url)
        if match:
            host = match.group(1)
            return host
        else:
            logger.exception("Invalid input. Matches does not found")
            raise Exception('Invalid input. Matches does not found')



