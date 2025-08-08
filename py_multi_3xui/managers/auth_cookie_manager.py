import time
import diskcache as dc
import pyotp
import requests

from py3xui import Api
import logging
logger = logging.getLogger(__name__)

cache_path = "/temp/cookie_cache"

class AuthCookieManager:
    @staticmethod
    def get_auth_cookie(server_dict:dict) -> str:
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
                if AuthCookieManager.check_auth_cookie(session=cookie,
                                                       host=host):
                    logger.debug("Got cookie from memory")
                    return cookie



        logger.debug("cookie was old/incorrect. creating new one.")
        connection = Api(host=host,
                         password=password,
                         username=admin_username,
                         use_tls_verify=use_tls_verification)
        created_at = time.time()
        totp = pyotp.TOTP(secret_token_for_2FA)
        connection.login(totp.now())
        logger.debug("new cookie acquired")
        new_cookie = {
            "value":connection.session,
            "created_at":created_at
        }
        cache.set(host,new_cookie,expire=3600)
        logger.info(f"updated cookie for {server_dict["host"]}")
        return new_cookie["value"]
    @staticmethod
    def check_auth_cookie(session:str,host:str):
        url = f"{host}/api/inbounds/list"
        headers = {
            'Cookie': f'session={session}'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                return False
            else:
                return False
        except requests.exceptions.RequestException as e:
            return False
    @staticmethod
    def clear_all_cookies():
        """
       Delete ALL cached cookie.
        """
        with dc.Cache(cache_path) as cache:
            cache.clear()
    @staticmethod
    def delete_cookie_by_host(host: str):
        """
        delete cookie for one server.
        """
        with dc.Cache(cache_path) as cache:
            cache.delete(host)
