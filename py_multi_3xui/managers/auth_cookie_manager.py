import time
import diskcache as dc
import pyotp
import requests

from py3xui import Api, AsyncApi
import logging
logger = logging.getLogger(__name__)

cache_path = "/temp/cookie_cache"

class AuthCookieManager:
    @staticmethod
    async def  get_logged_api(server_dict:dict) -> AsyncApi:
        """
        Get auth_cookie from cache. If it's too old or does not exist, then create a new one
        :param server_dict: a server in form of a dict
        :return: Auth cookie for 3xui panel
        """
        logger.debug(f"Getting auth_cookie for {server_dict["host"]}")
        host = server_dict["host"]
        password = server_dict["password"]
        admin_username = server_dict["admin_username"]
        use_tls_verification = bool(server_dict["use_tls_verification"])
        secret_token_for_2FA = server_dict["secret_token_for_2FA"]
        cache = dc.Cache(cache_path)
        cached = cache.get(host)
        if cached:
            age = time.time() - cached["created_at"]
            if age < 3600:
                cookie = cached["value"]
                logger.debug("Got auth from memory")
                return cookie
        logger.debug("auth was old/incorrect. creating new one.")
        connection = AsyncApi(host=host,
                         password=password,
                         username=admin_username,
                         use_tls_verify=use_tls_verification)
        created_at = time.time()
        totp = pyotp.TOTP(secret_token_for_2FA)
        await connection.login(totp.now())
        logger.debug("new auth acquired")
        new_cookie = {
            "value":connection,
            "created_at":created_at
        }
        cache.set(host,new_cookie,expire=3600)
        logger.info(f"updated auth for {server_dict["host"]}")
        return new_cookie["value"]
    @staticmethod
    def clear_all_auth():
        """
       Delete ALL cached auth.
        """
        with dc.Cache(cache_path) as cache:
            cache.clear()
    @staticmethod
    def delete_auth_by_host(host: str):
        """
        delete auth for one server.
        """
        with dc.Cache(cache_path) as cache:
            cache.delete(host)
