import time
import diskcache as dc

from py3xui import Api


class AuthCookieManager:
    @staticmethod
    def get_auth_cookie(server_params:dict) -> str:

        host = server_params["host"]
        password = server_params["password"]
        username = server_params["username"]
        secret_token = server_params["secret_token"]

        cache = dc.Cache("/temp/cookie_cache")
        cached = cache.get(host)
        if cached:
            age = time.time() - cached["created_at"]
            if age < 3600:
                return cached["value"]


        connection = Api(host=host,
                         password=password,
                         username=username,
                         token=secret_token)
        created_at = time.time()
        connection.login()
        new_cookie = {
            "value":connection.session,
            "created_at":created_at
        }
        cache.set(host,new_cookie,expire=3600)
        return new_cookie["value"]

