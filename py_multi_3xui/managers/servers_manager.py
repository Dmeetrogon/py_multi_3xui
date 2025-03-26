from py_multi_3xui.exceptions.exceptions import HostAlreadyExistException
import os
from contextlib import closing
from py_multi_3xui.server.server import Server
import sqlite3
class ServerDataManager:
    def __init__(self,path = "servers.db"):
        self.db_path = path
        with sqlite3.connect(self.db_path) as con:
            cursor = con.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS servers (country STRING,host STRING PRIMARY KEY,user STRING,password STRING,secret_token STRING,internet_speed INT)")
            con.commit()
    def add_server(self,server: Server):
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                try:
                    cursor.execute(f"INSERT INTO servers VALUES(? ,? ,? ,? ,?, ?)", (
                    server.location, server.host, server.username, server.password, server.secret_token,server.internet_speed))
                    connection.commit()
                except sqlite3.IntegrityError:
                    raise HostAlreadyExistException(f"Host {server.host} is already exist in database")
    def delete_server(self, host:str):
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"DELETE FROM servers WHERE host = '{host}'")
                connection.commit()
    def get_server_by_host(self,host:str) -> Server:
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM servers WHERE host = '{host}'")
                connection.commit()
                raw_tuple = cursor.fetchone()
                return Server.sqlite_answer_to_instance(raw_tuple)
    def get_available_countries(self):
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT DISTINCT country FROM servers")
                available = [row[0] for row in cursor.fetchall()]
                return available
    def get_servers_by_country(self,country:str) -> list[Server]:
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM servers WHERE country = '{country}'")
                raw_tuples = cursor.fetchall()
                servers_list = []
                for raw_tuple in raw_tuples:
                    servers_list.append(Server.sqlite_answer_to_instance(raw_tuple))
                connection.commit()
                return servers_list
    def get_all_servers(self):
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
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
        previous_best_server_stats = {"server":servers[0],
                                      "client_count":0}
        for server in servers:
            clients_on_server = 0
            api = server.connection
            try:
                inbounds = await api.inbound.get_list()
                for inbound in inbounds:
                    clients_on_server = clients_on_server + len(inbound.settings.clients)
            except:
                pass
            current_best_server = {"server":server,
                                    "client_count":clients_on_server}
            if current_best_server["client_count"] <= previous_best_server_stats["client_count"]:
                previous_best_server_stats = current_best_server
        best_server = previous_best_server_stats["server"]
        return best_server

