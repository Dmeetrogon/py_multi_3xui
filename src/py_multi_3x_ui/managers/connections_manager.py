from py3xui import AsyncApi, Client
from src.py_multi_3x_ui.server.server import Server
from src.py_multi_3x_ui.exceptions.exceptions import ClientNotFoundException
from server_data_manager import ServerDataManager
import uuid
class ConnectionsManager:
    async def choose_best_server(self,servers) -> Server:
        previous_best_server_stats = (servers[0],0)
        for server in servers:
            current_speed = server.internet_speed
            CLIENTS_PER_GB = 16 #16 clients can use 1 gb of the traffic speed with comfort|16 людей могут использовать 1 гб траффика с комфортом
            max_client_amount = current_speed * CLIENTS_PER_GB
            clients_on_server = 0
            api = AsyncApi(host=server.host,password=server.password,username=server.username,token=server.secret_token)
            try:
                await api.login()
                inbounds = await api.inbound.get_list()
                for inbound in inbounds:
                    clients_on_server = clients_on_server + len(inbound.settings.clients)
            except:
                pass
            if clients_on_server >= max_client_amount:
                continue
            current_server_stats = (server, clients_on_server)
            if current_server_stats[1] <= previous_best_server_stats:
                previous_best_server_stats = current_server_stats
        best_server = previous_best_server_stats[1]
        return best_server
    async def choose_best_server_by_country(self,country:str) -> Server:
        server_data_manager = ServerDataManager()
        servers =  server_data_manager.get_servers_by_country(country)
        best_server = await self.choose_best_server(servers)
        return  best_server
    async def add_client(self,server:Server,client_email:str,inbound_id = 4,expiry_time = 30) -> None:
         connection = AsyncApi(server.host,server.username,server.password,server.secret_token)
         await connection.login()
         client = Client(id=str(uuid.uuid4()),
                         email=client_email,
                         expiry_time=expiry_time,
                         enable=True,
                         flow="xtls-rprx-vision",
                         )
         connection.client.add(inbound_id=4,client=[client])
    async def update_client(self,server:Server, updated_client:Client) -> None:
        connection = AsyncApi(server.host, server.username, server.password, server.secret_token)
        await connection.login()
        connection.client.update(updated_client.id,updated_client)
    async def delete_client_by_uuid(self,server:Server,client_uuid:str,inbound_id = 4):
         connection = AsyncApi(server.host,server.username,server.password,server.secret_token)
         await connection.login()
         connection.client.delete(inbound_id=4,client_uuid=client_uuid)
    async def delete_client_by_email(self,server:Server,client_email:str,inbound_id = 4):
         connection = AsyncApi(server.host,server.username,server.password,server.secret_token)
         await connection.login()
         inbound = await connection.inbound.get_by_id(inbound_id)
         all_clients = inbound.settings.clients
         for client in all_clients:
             if client.email == client_email:
                 await self.delete_client_by_uuid(server,client.id,inbound_id)
         raise ClientNotFoundException(f'Client with email {client_email} not found')