import time
import diskcache as dc

from py_multi_3xui import Server
from py3xui import Api


class AuthCookieManager:
    @staticmethod
    def get_auth_cookie(server:Server) -> str:
        cache = dc.Cache("/temp/cookie_cache")
        cached = cache.get(server.host)
        if cached:
            age = time.time() - cached["created_at"]
            if age < 3600:
                return cached["value"]


        connection = Api(host=server.host,
                         password=server.password,
                         username=server.username,
                         token=server.secret_token)
        created_at = time.time()
        connection.login()
        new_cookie = {
            "value":connection.session,
            "created_at":created_at
        }
        cache.set(server.host,new_cookie,expire=3600)
        return new_cookie["value"]

