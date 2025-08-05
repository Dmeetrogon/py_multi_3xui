import json

from py3xui import Client

from py_multi_3xui.exceptions.exceptions import HostAlreadyExistException
from py_multi_3xui.server.server import Server
from py_multi_3xui.tools.enums import ExitDataFormat

from contextlib import closing
import xml.etree.ElementTree as ET
from functools import  singledispatchmethod

import sqlite3
import logging
logger = logging.getLogger(__name__)

class ServerDataManager:
    def __init__(self,path = "servers.db"):
        """
        This constructor firstly initializing .db file and then connecting to database
        :param path: the path of db.
        """
        self.db_path = path
        with sqlite3.connect(self.db_path) as con:
            cursor = con.cursor()
            logger.debug("connect to db. also creating it, if it does not exist")
            cursor.execute("CREATE TABLE IF NOT EXISTS servers (location STRING,host STRING PRIMARY KEY,user STRING,password STRING,internet_speed INT)")
            con.commit()

    @singledispatchmethod
    def add_server(self,arg):
        """
        Nothing here.
        :return: None
        """
        pass
    @add_server.register
    def _(self,server: Server):
        """
        Adds a server to a SQL database

        :param server: py_multi_3xui.Server instance
        :raises HostAlreadyExistException: if server(it's host) already exist in database
        :return: None
        """
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                try:
                    logger.debug("add server to db")
                    cursor.execute(f"INSERT INTO servers VALUES(? ,? ,? ,? ,?)", (
                    server.location, server.host, server.admin_username, server.password, server.internet_speed))
                    connection.commit()
                    logger.debug("successfully add")
                except sqlite3.IntegrityError as e:
                    logger.error(f"an error occurred: {e}.")
                    raise HostAlreadyExistException(f"Host {server.host} is already exist in database")
    @add_server.register
    def _(self,
                   location:str,
                   host:str,
                   admin_user:str,
                   password:str,
                   internet_speed:int,
                   use_tls_verification:bool = True):
        """
               Adds a server to a SQL database from server's properties

               :param location: location
               :param host: host(ip or web address)
               :param admin_user: username to access the 3xui
               :param password: password to access 3xui
               :param internet_speed: server's internet speed in GB/sec
               :param use_tls_verification: use TLS verification(optional). Don't change if not needed
               :raises HostAlreadyExistException: raises if server(it's host) already exist in database
               :return: None
               """
        server = Server(location=location,
                        password=password,
                        internet_speed=internet_speed,
                        use_tls_verification=use_tls_verification,
                        host=host,
                        admin_username= admin_user)
        self.add_server(server=server)
    @add_server.register
    def _(self, json_str:str):
        server = Server.from_json(json_str)
        self.add_server(server)
    def delete_server(self, host:str):
        """
        Deletes server by its host from database

        :param host: host for deletion the server from database
        :return: None
        """
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                logger.debug("Delete server from db")
                cursor.execute(f"DELETE FROM servers WHERE host = ?",(host,))
                connection.commit()
                logger.debug("Successfully delete")
    def get_server_by_host(self,host:str) -> Server:
        """
        Get server instance from database by its host

        :param host: server's host
        :return: py_multi_3xui.Server instance
        """
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:
                logger.debug("get server by host")
                sql_query = "SELECT * FROM servers WHERE host LIKE ?"
                search_pattern = f'%{host}%'
                cursor.execute(sql_query, (search_pattern,))
                connection.commit()
                raw_tuple = cursor.fetchone()
                logger.debug("successfully get server in the form of tuple")
                return Server.sqlite_answer_to_instance(raw_tuple)
    def get_available_locations(self):
        """
        Get distinct LOCATIONS from database
        :return: list of all possible locations
        """
        with closing(sqlite3.connect(f"{self.db_path}")) as connection:
            with closing(connection.cursor()) as cursor:

                logger.debug("get available locations")

                cursor.execute("SELECT DISTINCT location FROM servers")
                available = [row[0] for row in cursor.fetchall()]

                logger.debug("successfully get available locations")

                return available
    def get_servers_by_location(self,location:str) -> list[Server]:
        """
        Gets all servers in location
        :param location:
        :return: list of servers(instances) in chosen location
        """
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
        """
        Get all servers from database
        :return: list of all servers
        """
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
        """
        Get best server by its location based on its client_count/internet_speed ratio.
        :param location: location
        :return: the best server
        """
        logger.debug("get best server by location")
        servers = self.get_servers_by_location(location)
        best_server = await self.choose_best_server(servers)
        return  best_server
    @staticmethod
    async def choose_best_server(servers:list[Server]) -> Server:
        """
        Get the best server based on its client_count/internet_speed ratio
        :param servers: list of server instances
        :return: the best server based on client_count/internet_speed ratio
        """
        logger.debug("choose best server by list of servers")
        best_server_stats = {"server":servers[0],
                                      "traffic_per_client":0}
        for server in servers:
            total_clients = server.get_amount_of_client()
            traffic_per_client = server.internet_speed / total_clients
            curr_server = {"server":server,
                                    "traffic_per_client":traffic_per_client}
            if curr_server["traffic_per_client"] > best_server_stats["traffic_per_client"]:
                best_server_stats = curr_server
        logger.debug("Get best server")
        best_server = best_server_stats["server"]
        return best_server
    @staticmethod
    async def get_server_info(exit_format:ExitDataFormat,
                              server:Server):
        """
        Converts server's info into the chosen format(Json, String, XML)

        :param exit_format: a type of exit data
        :param server: server
        :return: server's properties in chosen format
        """
        api = server.connection
        inbounds = await api.inbound.get_list()
        amount_of_inbounds =  len(inbounds)
        amount_of_clients = await server.get_amount_of_client()
        usage_ratio = amount_of_clients / server.internet_speed
        if exit_format == ExitDataFormat.STRING:
            output_string = ("Standard info:\n" +
                             server.__str__() +
                             f"\nAmount of inbounds: {amount_of_inbounds}" +
                             f"\nAmount of clients: {amount_of_clients}" +
                             f"\nClients per GB/sec ratio: {usage_ratio}" +
                             f"For more information visit your panel")
            return output_string
        elif exit_format == ExitDataFormat.JSON:
            dynamic_data = \
                {
                    "inbounds_count":amount_of_inbounds,
                    "clients_count":amount_of_clients,
                    "usage_ratio": usage_ratio
                }
            output_string = \
                {
                    "server_fields":server.to_json(),
                    "dynamic_data":dynamic_data
                }
            return json.dumps(output_string,indent=2)
        elif exit_format == ExitDataFormat.XML:
            root = ET.Element("data")
            dynamic_data = \
                {
                    "inbounds_count": amount_of_inbounds,
                    "clients_count": amount_of_clients,
                    "usage_ratio": usage_ratio
                }
            server_elem = ET.SubElement(root, "server")
            for key, value in server.to_json().items():
                sub = ET.SubElement(server_elem, key)
                sub.text = str(value)
            dynamic_elem = ET.SubElement(root, "dynamic")
            for key, value in dynamic_data.items():
                sub = ET.SubElement(dynamic_elem, key)
                sub.text = str(value)
            return ET.tostring(root, encoding="unicode", method="xml")