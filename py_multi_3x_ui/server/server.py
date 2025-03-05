import requests
from py_multi_3x_ui.exceptions.exceptions import ClientNotFoundException
from py3xui import Client,AsyncApi
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
        if not self.__connection.session and self.__check_if_connection_is_available():
            self.__connection.login()
        return self.__connection
    @staticmethod
    def sqlite_answer_to_instance(answer:tuple):
        return Server(answer[0],answer[1],answer[2],answer[3],answer[4],answer[5])
    async def __check_if_connection_is_available(self):
        try:
            self.__connection.inbound.get_list()
        except requests.RequestException:
            return False
        return True
    def __str__(self):
        return f"{self.host}\n{self.username}\n{self.password}\n{self.secret_token}\n{self.location}\n{self.internet_speed}"
    async def add_client(self,client_email:str,inbound_id = 4,expiry_time = 30) -> None:
         connection =  self.connection
         client = Client(id=str(uuid.uuid4()),
                         email=client_email,
                         expiry_time=expiry_time,
                         enable=True,
                         flow="xtls-rprx-vision",
                         )
         connection.client.add(inbound_id=inbound_id,client=[client])
    async def update_client(self, updated_client:Client) -> None:
        connection = self.connection
        connection.client.update(updated_client.id,updated_client)
    async def delete_client_by_uuid(self,client_uuid:str,inbound_id = 4) -> None:
         connection = self.connection
         connection.client.delete(inbound_id=inbound_id,client_uuid=client_uuid)
    async def delete_client_by_email(self,client_email:str,inbound_id = 4) -> None:
         connection =  self.connection
         inbound = await connection.inbound.get_by_id(inbound_id)
         all_clients = inbound.settings.clients
         for client in all_clients:
             if client.email == client_email:
                 await self.delete_client_by_uuid(client.id,inbound_id)
         raise ClientNotFoundException(f'Client with email {client_email} not found')
    async def send_backup(self) -> None:
        connection = self.connection
        connection.database.export()