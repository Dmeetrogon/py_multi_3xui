import json

from py3xui import Client,Inbound, AsyncApi

from py_multi_3xui.tools.regular_expressions import RegularExpressions as regularExpressions
from py_multi_3xui.tools.converter import Converter
from py_multi_3xui.managers.auth_cookie_manager import AuthCookieManager as cookieManager
from py_multi_3xui.exceptions.exceptions import ServerNotFoundException

import uuid
import logging

logger = logging.getLogger(__name__)

class Server:
    def __init__(self,location:str,host:str,admin_username:str,password:str,internet_speed:int,use_tls_verification:bool = True):
        logger.debug("create server instance")
        self.__use_tls_verification = use_tls_verification
        self.__location = location
        self.__host = host
        self.__password = password
        self.__admin_username = admin_username
        self.__internet_speed = internet_speed
        self.__connection = AsyncApi(host=host,
                                     password=password,
                                     use_tls_verify=use_tls_verification,
                                     username=admin_username)
    @property
    def location(self):
        return self.__location
    @location.setter
    def location(self,value):
        self.__location = value

    @property
    def host(self):
        return self.__host
    @host.setter
    def host(self,value):
        self.__host = value

    @property
    def use_tls_verification(self):
        return self.__use_tls_verification
    @use_tls_verification.setter
    def use_tls_verification(self,value):
        logger.warning("it is not recommended to change 'use_tls_verification' property.")
        if value != self.__use_tls_verification:
            self.__connection = AsyncApi(self.host,self.admin_username,self.password,value)
        self.__use_tls_verification = value
    @property
    def password(self):
        return self.__password
    @password.setter
    def password(self,value):
        self.__password = value
    @property
    def admin_username(self):
        return self.__admin_username
    @admin_username.setter
    def admin_username(self,value):
        self.__admin_username = value
    @property
    def internet_speed(self):
        return self.__internet_speed
    @internet_speed.setter
    def internet_speed(self,value):
        self.__internet_speed = value
    @property
    def connection(self):
        logger.debug("Try to get a server cookie. Redirecting to AuthCookieManager")
        cookie = cookieManager.get_auth_cookie(server_dict=self.to_dict())
        self.__connection.session = cookie
        logger.debug("Get cookie")
        return self.__connection

    def check_connection(self):
        """
        Check availability of the 3xui panel
        :return: Availability
        """
        try:
            conn = self.connection
            conn.inbound.get_list()
            logger.debug(f"successfully connect to {self.host}")
            return True
        except Exception as e:
            logger.warning(f"Cannot to connect {self.host}. Reason: {e}")
            return False
    def to_dict(self) -> dict[str,str|int|None]:
        """
        Converts servers instance to a dict
        :return: a server in form of a dict
        """
        logger.debug("Convert server's instance to dict")
        return {
            "location":self.location,
            "host":self.host,
            "password":self.password,
            "admin_username":self.admin_username,
            "internet_speed":self.internet_speed,
            "use_tls_verification":self.use_tls_verification
        }
    def to_json(self):
        """
        Converts server to JSON string
        :return: JSON str
        """
        str_json = self.to_dict()
        return json.dumps(str_json)
    def __str__(self):
        logger.debug("Convert server to str")
        return f"{self.host}\n{self.admin_username}\n{self.password}\n{self.location}\n{self.internet_speed}\n"

    async def add_client(self,client:Client):
        """
        Add client to a server(indound_id is in the client instance)
        :param client: py3xui.Client
        :return: None
        """
        connection = self.connection
        await connection.client.add(inbound_id=client.inbound_id,clients=[client])
    async def get_amount_of_client(self):
        """
        Get amount of clients of the server
        :return: Total amount of clients
        """
        total_clients = 0
        api = self.connection
        inbounds = await api.inbound.get_list()
        for inbound in inbounds:
             try:
                total_clients += len(inbound.settings.clients)
             except Exception as e:
                logger.warning(f"An exception occurred: {e}. Ignoring it.")
                pass
        return  total_clients
    async def update_client(self, updated_client: Client) -> None:
        """
        Update client by its new instance

        :param updated_client: a new(updated) instance of a py3xui Client
        :return: None
        """
        logger.debug("update client")
        connection = self.connection
        inbound = connection.inbound.get_by_id(inbound_id=updated_client.inbound_id)
        user_email = updated_client.email
        client_uuid = None
        for c in inbound.settings.clients:
            if c.email == user_email:
                client_uuid = c.id
                break
        await connection.client.update(client_uuid, updated_client)
    async def get_config(self,client:Client):
        """
        Get string config by client instance.
        (always configure the panel so that VLESS listens on port 443)
        :param client: py3xui client
        :return: string config
        """
        logger.debug("generate str config")
        connection = self.connection
        inbound = await connection.inbound.get_by_id(inbound_id=client.inbound_id)
        public_key =  inbound.stream_settings.reality_settings.get("settings").get("publicKey")
        website_name = inbound.stream_settings.reality_settings.get("serverNames")[0]
        short_id = inbound.stream_settings.reality_settings.get("shortIds")[0]
        user_uuid = str(uuid.uuid4())
        full_host_name = regularExpressions.get_host(self.host)
        connection_string = (
            f"vless://{user_uuid}@{full_host_name}:443"#vless + reality always listens on 443 port(normal ppl do like that)
            f"?type=tcp&security=reality&pbk={public_key}&fp=random&sni={website_name}"
            f"&sid={short_id}&spx=%2F#DeminVPN-{client.email}"
        )
        return connection_string
    async def get_inbounds(self) -> list[Inbound]:
        """
        Get panel's inbounds
        :return: A list of inbounds
        """
        logger.debug("get inbounds")
        return await self.connection.inbound.get_list()
    async def get_inbound_by_id(self,inbound_id: int) -> Inbound:
        """
        Get inbound by its id

        :param inbound_id: an inbound ID
        :return: None
        """
        logger.debug("get inbound by id")
        inbound = await self.connection.inbound.get_by_id(inbound_id)
        return inbound
    async def get_client_by_email(self,email :str) -> Client:
        """
        Get client by its email
        :param email: client email(unique for panel, not inbounds)
        :return: Client
        """
        logger.debug("get client by email")
        client =  await self.connection.client.get_by_email(email)
        return client
    def delete_client_by_uuid(self,client_uuid:str,
                                    inbound_id:int) -> None:
        """
        Delete client by its uuid
        :param client_uuid: client uuid
        :param inbound_id: inbound id
        :return: None
        """
        logger.debug("delete client via uuid")
        connection = self.connection
        connection.client.delete(inbound_id=inbound_id,client_uuid=client_uuid)
    async def delete_client_by_email(self,client_email:str) -> None:
        logger.debug("delete client by email")
        connection =  self.connection
        client = await connection.client.get_by_email(client_email)
        client_uuid = client.id
        inbound_id = client.inbound_id
        self.delete_client_by_uuid(client_uuid,inbound_id)
    def send_backup(self) -> None:
        """
        Send a backup of a 3xui panel to admins in Telegram bot
        :return: None
        """
        logger.debug("send backup to admins")
        connection = self.connection
        connection.database.export()
    @staticmethod
    def sqlite_answer_to_instance(answer: tuple):
        """
        Converts a server if a form of a tuple to an instance
        :param answer:
        :return:
        """
        logger.debug("convert tuple to server instance")
        if answer is None:
            raise ServerNotFoundException("Server wasn't found in the db")
        return Server(answer[0], answer[1], answer[2], answer[3], answer[4], answer[5])
    @classmethod
    def from_dict(cls, server: dict[str, str | int | None]):
        """
        Converts a dict to a server instance
        :param server: server dictionary
        :return:
        """
        logger.debug("convert dict to instance")
        location = server["location"]
        host = server["host"]
        password = server["password"]
        admin_username = server["admin_username"]
        internet_speed = server["internet_speed"]
        use_tls_verification = bool(server["use_tls_verification"])
        return Server(host=host,
                      location=location,
                      admin_username=admin_username,
                      password=password,
                      internet_speed=internet_speed,
                      use_tls_verification=use_tls_verification)
    @classmethod
    def from_json(cls, server_json: str):
        data = json.loads(server_json)
        return cls.from_dict(data)
    @staticmethod
    def generate_client(client_email: str
                        , inbound_id: int
                        , expiry_time=30
                        , limit_ip=0
                        , total_gb=0
                        , up=0
                        , down=0
                        ) -> Client:
        """
        Generate(NOT ADD) py3xui client from its properties
        Visit https://github.com/iwatkot/py3xui for more info about py3xui.Client instance and its properties

        :param client_email: client's email. Must be unique
        :param inbound_id: inbound_id
        :param expiry_time: expiry_time in days
        :param limit_ip: a max amount of a client's ip. If set to zero - no restrictions
        :param total_gb: max amount of traffic
        :param up: restriction on upload speed
        :param down: restriction on download speed
        :return: py3xui.Client.
        """
        logger.info("Generate client")
        # calculating how much the client will live(sound kinda sounds ambiguous,lol)
        total_time = Converter.convert_days_to_valid_3xui_time(expiry_time)
        client = Client(id=str(uuid.uuid4()),
                        email=client_email,
                        expiry_time=total_time,
                        enable=True,
                        flow="xtls-rprx-vision",
                        inbound_id=inbound_id,
                        limit_ip=limit_ip,
                        total_gb=total_gb,
                        up=up,
                        down=down
                        )
        return client


