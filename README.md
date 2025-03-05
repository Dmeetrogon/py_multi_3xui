# multi_3x_ui
A tool for managing multiple 3x-ui panels at once.
## Overview
This module is based on [py3xui](https://github.com/iwatkot/py3xui).\
Used dependencies:
-  `py3xui` for connecting and managing 3xui panels
- - `py3xui` dependencies:
- - `requests` for synchronous API
- - `httpx` for asynchronous API
- - `pydantic` for models
-  `six` (I just cannot make py3xui work without a last version of six. This will be fixed in next versions)

Supported Python Versions:
-  `3.11 `
-  `3.12 `

3x-ui is under development. py3xui also. I am not related with 3x-ui or py3xui. But the module supports py3xui>=0.3.4(and all version of 3x-ui that being supported by py3xui)
# Quick Start
### Installation
 ```bash
pip install py_multi_3xui
```
### Adding server to database

```python
from py_multi_3x_ui import Server
from py_multi_3x_ui import ServerDataManager
username = "Ben"
password = "BenLoveApples123"
host = "https://benserver.com:PORT/PATH/"
secret_token = "very_secret_token"
internet_speed = 5#amount in gb per second.
location = "usa"
# to add a server to db you need to create an instance of server
server = Server(username=username,password=password,host=host,location=location,secret_token=secret_token,internet_speed=internet_speed)
data_manager = ServerDataManager()
#after first call ServerDataManager.__init__() the servers.db will be created(if it already exists, it won't be created)
data_manager.add_server(server)
```

some notes:
- *Learn your server's traffic speed by using [Ookla](https://www.speedtest.net/) or ask your VPS seller. This is used to calculate a comfortable amount of users per server*
- *note, that there is no filtration by valid country code. You can add whatever location that you want(maybe will be improved)*

### Deleting server from database

```python
from py_multi_3x_ui import ServerDataManager
host = "some_server.com:PORT/PATH/"
manager = ServerDataManager()
manager.delete_server(host)
```
## Operating with servers

### Get best server by country
```python
from py_multi_3x_ui import ServerDataManager
manager = ServerDataManager()
country = "usa"
best_server = await manager.choose_best_server_by_country("usa")
print(best_server.__str__())
```
### Add client

```python
server = ...
client_email = "some_email"
expiry_time = 30#in days
inbound_id = 4# by default inbound id is set to 4
server.add_client(client_email=client_email,expiry_time=expiry_time,inbound_id=inbound_id)
```
### Delete client by uuid
```python
server = ...
uuid = "27b7a601-31d9-42af-8f74-4511092af5d4"
inbound_id = 4
server.delete_client_by_uuid(client_uuid=uuid,inbound_id=inbound_id)
```
# Bugs and Features
 - - -
Please report any bugs or feature requests by opening an issue on [GitHub issues](https://github.com/Dmeetrogon/py_multi_3xui/issues)













