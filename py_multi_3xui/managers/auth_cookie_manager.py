import time
import diskcache as dc

from py3xui import Api
import logging
logger = logging.getLogger(__name__)

class AuthCookieManager:
    @staticmethod
    def get_auth_cookie(server_dict:dict) -> str:
        """
        Get auth_cookie from cache. If it too old or does not exist, then create a new one
        :param server_dict: a server in form of a dict
        :return: Auth cookie for 3xui panel
        """
        logger.debug(f"Getting auth_cookie for {server_dict["host"]}")
        host = server_dict["host"]
        password = server_dict["password"]
        admin_username = server_dict["admin_username"]
        secret_token = server_dict["secret_token"]
        use_tls_verification = bool(server_dict["use_tls_verification"])

        cache = dc.Cache("/temp/cookie_cache")
        cached = cache.get(host)
        if cached:
            age = time.time() - cached["created_at"]
            if age < 3600:
                logger.debug("Got cookie from memory")
                return cached["value"]
        logger.debug("cookie was too old or it doesnt exist. creating new one.")
        connection = Api(host=host,
                         password=password,
                         username=admin_username,
                         token=secret_token,
                         use_tls_verify=use_tls_verification)
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




