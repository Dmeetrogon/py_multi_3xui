import time
import diskcache as dc

from py3xui import Api
import logging
logger = logging.getLogger(__name__)

class AuthCookieManager:
    @staticmethod
    def get_auth_cookie(server_dict:dict) -> str:
        logger.debug(f"Get auth_cookie for {server_dict["host"]}")
        host = server_dict["host"]
        password = server_dict["password"]
        username = server_dict["username"]
        secret_token = server_dict["secret_token"]

        cache = dc.Cache("/temp/cookie_cache")
        cached = cache.get(host)
        if cached:
            age = time.time() - cached["created_at"]
            if age < 3600:
                logger.debug("Got cookie from memory")
                return cached["value"]
        logger.debug("cookie was too old. refreshing it.")

        connection = Api(host=host,
                         password=password,
                         username=username,
                         token=secret_token)
        created_at = time.time()
        connection.login()
        logger.debug("new cookie acquired")
        new_cookie = {
            "value":connection.session,
            "created_at":created_at
        }
        cache.set(host,new_cookie,expire=3600)
        logger.info(f"updated cookie for {server_dict["host"]}")
        return new_cookie["value"]

