
# multi_3x_ui
A tool for managing multiple 3x-ui panels at once. 
## Overview
This module is based on [py3xui](https://github.com/iwatkot/py3xui).
Used dependencies:
-  `py3xui` for connecting and managing 3xui panels
- - `py3xui` dependencies:
    - - `requests` for synchronous API
    - - `httpx` for asynchronous API
    - - `pydantic` for models
-  `diskcache` for storing 3xui cookies

Supported Python Versions:
-  `3.11 `
-  `3.12 `

License:
- MIT License


**_3x-ui is under development. py3xui also. I am not related with 3x-ui or py3xui. But the module supports py3xui>=0.3.4(and all version of 3x-ui that are being supported by py3xui)_**
# Quick Start
### Installation
 ```bash
pip install py_multi_3xui
```

## Operating with servers

### Adding server to database

```python
from py_multi_3xui import Server
from py_multi_3xui import ServerDataManager

username = "Ben"
password = "BenLoveApples123"
host = "https://benserver.com:PORT/PATH/"
secret_token = "very_secret_token"
internet_speed = 5  # amount in gb per second.
location = "usa"

# to add a server to the db you need to create an instance of a server
server = Server(username=username, password=password, host=host, location=location, secret_token=secret_token,
                internet_speed=internet_speed)

data_manager = ServerDataManager()
# after first call ServerDataManager.__init__() the servers.db will be created(if it already exists, it won't be created)
data_manager.add_server(server)
```

some notes:
- *Learn your server's traffic speed by using [Ookla](https://www.speedtest.net/) or ask your VPS seller. This is used to calculate a comfortable amount of users per server*
- *note, that there is no filtration by valid country code. You can add whatever location that you want(maybe will be improved)*

### Deleting server from database

```python
from py_multi_3xui import ServerDataManager

host = "some_server.com:PORT/PATH/"#if you didnt specify a path it will be just "some_server.com:PORT"
manager = ServerDataManager()
manager.delete_server(host)
```
### Get best server by country

```python
from py_multi_3xui import ServerDataManager

manager = ServerDataManager()
location = "usa"
best_server = await manager.choose_best_server_by_location(location)
print(best_server.__str__())
```
## Working with clients/configs
### Generate client (not add)
```python
server = ...
# 1. Create client by yourself

from py3xui import Client

client = Client()

# 2. Create client using server.generate_client
from py_multi_3xui import RandomStuffGenerator as rsg

total_gb = 30  # max amount of traffic that can be used by client
inbound_id = 4  # client's inbound id
limit_ip = 0  # max amount of clients IP's. If set to zero, there is no limit
client_email = rsg.generate_email(10)  # client's email. Must be unique 
expiry_time = 30# expiry time in days. If set to zero, there is no limit
up = 0# a limit for upload speed. If set to zero, there is no limit
down = 0# a limit for download speed. If set to zero, there is no limit
client = server.generate_client(total_gb=total_gb,
                                inbound_id=inbound_id,
                                limit_ip=limit_ip,
                                client_email=client_email,
                                expiry_time=expiry_time,
                                up=up,
                                down=down)  # note, this method is static
```
note: _For more complete info about **py3xui.Client** visit [py3xui documentation](https://github.com/iwatkot/py3xui)_
### Add client to server
```python
from py_multi_3xui import Server
from py3xui import Client
server = ...
client = ...
server.add_client(client)
```
### Edit/Update client
```python
from py3xui import Client
server = ...
client = await server.get_client_by_email("some_email")
#then you edit client's fields
client.up = 50
client.down = 30
#and finally update
server.update_client(client)
```


### Get connection string
```python
from py_multi_3xui import Server
from py3xui import Client
server = ...
client = ...
config = server.get_config(client)
```
### Delete client by uuid
```python
server = ...
uuid = "some uuid"
inbound_id = 4
server.delete_client_by_uuid(client_uuid=uuid,inbound_id=inbound_id)
```

# Bugs and Features
 - - -
Please report any bugs or feature requests by opening an issue on [GitHub issues](https://github.com/Dmeetrogon/py_multi_3xui/issues)
(or you can DM me via Telegram: https://t.me/dmeetrogon)

## Donate and support
_If this project was helpful for you, you may wish star it or donate ^^_

* **via [CryptoBot](https://t.me/send?start=IVFCR3tEjcyk)**
* **via Ton: `UQCOKDO9dRYNe3Us8FDK2Ctz6B4fhsonaoKpK93bqneFAyJL`**

## Plans:

1.  Add manual
2.  Add better logging
3.  Do code review and refactoring
4.  Add ability to work not only with VLESS configs
5.  Improve server.py
6.  Improve database handle(add encryption,verification and etc)












