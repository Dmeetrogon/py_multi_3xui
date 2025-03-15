from py_multi_3xui.exceptions.exceptions import HostAlreadyExistException
from contextlib import closing
from py3xui import AsyncApi
from py_multi_3xui.server.server import Server
import os
import sqlite3
class ServerDataManager:
    def __init__(self,db_name = "servers"):
        self.db_name = db_name
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "servers.db")
        with sqlite3.connect(db_path) as con:
            cursor = con.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS servers (country STRING,host STRING PRIMARY KEY,user STRING,password STRING,secret_token STRING,internet_speed INT)")
            con.commit()
    def add_server(self,server: Server):
        with closing(sqlite3.connect(f"{self.db_name}.db")) as connection:
            with closing(connection.cursor()) as cursor:
                try:
                    cursor.execute(f"INSERT INTO servers VALUES(? ,? ,? ,? ,?, ?)", (
                    server.location, server.host, server.username, server.password, server.secret_token,server.internet_speed))
                    connection.commit()
                except sqlite3.IntegrityError:
                    raise HostAlreadyExistException(f"Host {server.host} is already exist in database")
    def delete_server(self, host:str):
        with closing(sqlite3.connect(f"{self.db_name}.db")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"DELETE FROM servers WHERE host = '{host}'")
                connection.commit()
    def get_server_by_host(self,host:str) -> Server:
        with closing(sqlite3.connect(f"{self.db_name}.db")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM servers WHERE host = '{host}'")
                connection.commit()
                raw_tuple = cursor.fetchone()
                return Server.sqlite_answer_to_instance(raw_tuple)
    def get_servers_by_country(self,country:str) -> list[Server]:
        with closing(sqlite3.connect(f"{self.db_name}.db")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM servers WHERE country = '{country}'")
                raw_tuples = cursor.fetchall()
                servers_list = []
                for raw_tuple in raw_tuples:
                    servers_list.append(Server.sqlite_answer_to_instance(raw_tuple))
                connection.commit()
                return servers_list
    def get_all_servers(self):
        with closing(sqlite3.connect(f"{self.db_name}.db")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM servers")
                raw_tuples = cursor.fetchall()
                servers_list = []
                for raw_tuple in raw_tuples:
                    servers_list.append(Server.sqlite_answer_to_instance(raw_tuple))
                connection.commit()
                return servers_list
    async def choose_best_server_by_country(self,country:str) -> Server:
        servers =  self.get_servers_by_country(country)
        best_server = await self.choose_best_server(servers)
        return  best_server
    @staticmethod
    async def choose_best_server(servers) -> Server:
        previous_best_server_stats = (servers[0], 0)
        for server in servers:
            clients_on_server = 0
            api = server.connection
            try:
                inbounds = await api.inbound.get_list()
                for inbound in inbounds:
                    clients_on_server = clients_on_server + len(inbound.settings.clients)
            except:
                pass
            current_server_stats = (server, clients_on_server)
            if current_server_stats[1] <= previous_best_server_stats:
                previous_best_server_stats = current_server_stats
        best_server = previous_best_server_stats[1]
        return best_server

