from py3xui import Client,Inbound, AsyncApi

from py_multi_3xui.tools.regular_expressions import RegularExpressions as regularExpressions
from py_multi_3xui.managers.auth_cookie_manager import AuthCookieManager as cookieManager

import uuid
class Server:
    def __init__(self,location:str,host:str,username:str,password:str,internet_speed:int,secret_token:str = None):
        self.__location = location
        self.__host = host
        self.__password = password
        self.__username = username
        self.__secret_token = secret_token
        self.__internet_speed = internet_speed
        self.__connection = AsyncApi(host,username,password,secret_token)
    @property
    def location(self):
        return self.__location
    @property
    def host(self):
        return self.__host
    @property
    def password(self):
        return self.__password
    @property
    def username(self):
        return self.__username
    @property
    def secret_token(self):
        return self.__secret_token
    @property
    def internet_speed(self):
        return self.__internet_speed
    @property
    def connection(self):
        cookie = cookieManager.get_auth_cookie(server_dict=self.to_dict())
        self.__connection.session = cookie
        return self.__connection
    def to_dict(self) -> dict[str,str|int|None]:
        return {
            "location":self.location,
            "host":self.host,
            "password":self.password,
            "username":self.username,
            "secret_token":self.secret_token,
            "internet_speed":self.internet_speed
        }
    def __str__(self):
        return f"{self.host}\n{self.username}\n{self.password}\n{self.secret_token}\n{self.location}\n{self.internet_speed}"
    @staticmethod
    def sqlite_answer_to_instance(answer:tuple):
        return Server(answer[0],answer[1],answer[2],answer[3],answer[4],answer[5])
    @staticmethod
    def from_dict(server:dict[str,str|int|None]):
        location = server["location"]
        host = server["host"]
        password = server["password"]
        username = server["username"]
        secret_token = server["secret_token"]
        internet_speed = server["internet_speed"]
        return Server(host=host,
                      location=location,
                      username=username,
                      password=password,
                      secret_token=secret_token,
                      internet_speed=internet_speed)
    @staticmethod
    def generate_client(client_email:str
                         ,inbound_id = 4
                         ,expiry_time = 30
                         ,limit_ip = 0
                         ,total_gb = 0
                         ,up = 0
                         ,down = 0
                         ) -> Client:
         client = Client(id=str(uuid.uuid4()),
                         email=client_email,
                         expiry_time=expiry_time,
                         enable=True,
                         flow="xtls-rprx-vision",
                         inbound_id=inbound_id,
                         limit_ip=limit_ip,
                         total_gb=total_gb,
                         up=up,
                         down=down
                         )
         return client
    async def add_client(self,client:Client):
        connection = self.connection
        await connection.client.add(inbound_id=client.inbound_id,clients=[client])
    async def get_config(self,client:Client):
        connection = self.connection
        inbound = await connection.inbound.get_by_id(inbound_id=client.inbound_id)
        public_key =  inbound.stream_settings.reality_settings.get("settings").get("publicKey")
        website_name = inbound.stream_settings.reality_settings.get("serverNames")[0]
        short_id = inbound.stream_settings.reality_settings.get("shortIds")[0]
        user_uuid = str(uuid.uuid4())
        full_host_name = regularExpressions.get_host(self.host)
        connection_string = (
            f"vless://{user_uuid}@{full_host_name}:443"#vless always listens on 443 port(normal ppl do like that)
            f"?type=tcp&security=reality&pbk={public_key}&fp=random&sni={website_name}"
            f"&sid={short_id}&spx=%2F#DeminVPN-{client.email}"
        )
        return connection_string
    async def get_inbounds(self) -> list[Inbound]:
        return await self.connection.inbound.get_list()
    async def get_inbound_by_id(self,inbound_id: int) -> Inbound:
        inbound = await self.connection.inbound.get_by_id(inbound_id)
        return inbound
    async def get_client_by_email(self,email :str) -> Client:
        client =  await self.connection.client.get_by_email(email)
        return client
    def update_client(self, updated_client:Client) -> None:
        connection = self.connection
        connection.client.update(updated_client.id,updated_client)
    def delete_client_by_uuid(self,client_uuid:str,
                                    inbound_id:int) -> None:
         connection = self.connection
         connection.client.delete(inbound_id=inbound_id,client_uuid=client_uuid)
    async def delete_client_by_email(self,client_email:str) -> None:
         connection =  self.connection
         client = await connection.client.get_by_email(client_email)
         client_uuid = client.id
         inbound_id = client.inbound_id
         self.delete_client_by_uuid(client_uuid,inbound_id)
    def send_backup(self) -> None:
        connection = self.connection
        connection.database.export()


