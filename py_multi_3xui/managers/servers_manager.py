from py_multi_3xui.exceptions.exceptions import HostAlreadyExistException
from py_multi_3xui.server.server import Server

from contextlib import closing

import sqlite3
import logging
logger = logging.getLogger(__name__)

class ServerDataManager:
    def __init__(self,path = "servers.db"):
        self.db_path = path
        with sqlite3.connect(self.db_path) as con:
            cursor = con.cursor()
            logger.debug("connect to db. also creating it, if it does not exist")
            cursor.execute("CREATE TABLE IF NOT EXISTS servers (location STRING,host STRING PRIMARY KEY,user STRING,password STRING,internet_speed INT,secret_token STRING)")
            con.commit()
    def add_server(self,server: Server):
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                try:
                    logger.debug("add server to db")
                    cursor.execute(f"INSERT INTO servers VALUES(? ,? ,? ,? ,?, ?)", (
                    server.location, server.host, server.username, server.password, server.internet_speed,server.secret_token))
                    connection.commit()
                    logger.debug("successfully add")
                except sqlite3.IntegrityError as e:
                    logger.error(f"an error occurred: {e}.")
                    raise HostAlreadyExistException(f"Host {server.host} is already exist in database")
    def delete_server(self, host:str):
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                logger.debug("Delete server from db")
                cursor.execute(f"DELETE FROM servers WHERE host = ?",(host,))
                connection.commit()
                logger.debug("Successfully delete")
    def get_server_by_host(self,host:str) -> Server:
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                logger.debug("get server by host")
                cursor.execute(f"SELECT * FROM servers WHERE host = ?",(host,))
                connection.commit()
                raw_tuple = cursor.fetchone()
                logger.debug("successfully get server in the form of tuple")
                return Server.sqlite_answer_to_instance(raw_tuple)
    def get_available_locations(self):
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:

                logger.debug("get available locations")

                cursor.execute("SELECT DISTINCT location FROM servers")
                available = [row[0] for row in cursor.fetchall()]

                logger.debug("successfully get available locations")

                return available
    def get_servers_by_location(self,location:str) -> list[Server]:
        servers_list = []
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                logger.debug("get servers by location")

                cursor.execute(f"SELECT * FROM servers WHERE location = ?",(location,))
                raw_tuples = cursor.fetchall()

                logger.debug("get list of server tuples")
                connection.commit()
        logger.debug("convert server tuples to objects")
        for raw_tuple in raw_tuples:
            servers_list.append(Server.sqlite_answer_to_instance(raw_tuple))
        return servers_list
    def get_all_servers(self):
        logger.debug("get all servers")
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM servers")
                raw_tuples = cursor.fetchall()
                servers_list = []
                connection.commit()
        logger.debug("got list of server tuples")
        logger.debug("Convert it to objects")
        for raw_tuple in raw_tuples:
                servers_list.append(Server.sqlite_answer_to_instance(raw_tuple))
        return servers_list
    async def choose_best_server_by_location(self,location:str) -> Server:
        logger.debug("get best server by location")
        servers = self.get_servers_by_location(location)
        best_server = await self.choose_best_server(servers)
        return  best_server
    @staticmethod
    async def choose_best_server(servers) -> Server:
        logger.debug("choose best server by list of servers")
        previous_best_server_stats = {"server":servers[0],
                                      "client_count":0}
        for server in servers:
            clients_on_server = 0
            try:
                api = server.connection
                inbounds = await api.inbound.get_list()
                for inbound in inbounds:
                    clients_on_server = clients_on_server + len(inbound.settings.clients)
            except Exception as e:
                logger.exception(f"An exception occurred: {e}. Ignoring it. Searching best server...")
                pass
            current_best_server = {"server":server,
                                    "client_count":clients_on_server}
            if current_best_server["client_count"] <= previous_best_server_stats["client_count"]:
                previous_best_server_stats = current_best_server
        logger.debug("Get best server")
        best_server = previous_best_server_stats["server"]
        return best_server