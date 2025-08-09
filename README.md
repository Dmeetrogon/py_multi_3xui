
<div align="center">

# multi_3x_ui  
**A tool for managing multiple 3x-ui panels at once**  

[![PyPI version](https://img.shields.io/pypi/v/py_multi_3xui.svg)](https://pypi.org/project/py_multi_3xui/)  
[![Python Versions](https://img.shields.io/pypi/pyversions/py_multi_3xui.svg)](https://www.python.org/)  
[![License](https://img.shields.io/github/license/Dmeetrogon/py_multi_3xui.svg)](LICENSE)  

</div>

---

> **Note:** Secret token feature was removed from 3x-ui in 2.6.0. From now this feature doesn't supported by py_multi_3xui and py3xui. Please, edit your constructors and databases

---

## 📚 Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Operating with servers](#operating-with-servers)
  - [Working with clients/configs](#working-with-clientsconfigs)
- [Bugs and Features](#bugs-and-features)
- [Donate and Support](#donate-and-support)
- [Plans](#plans)

---

## 📖 Overview
This module is based on **[py3xui](https://github.com/iwatkot/py3xui).** 

**Used dependencies:**
- `py3xui` for connecting and managing 3xui panels  
  - `requests` for synchronous API  
  - `httpx` for asynchronous API  
  - `pydantic` for models  
- `diskcache` for storing 3xui cookies  
- `pyotp` for getting OTP passwords based on string  

**Supported Python Versions:**
- `3.11`
- `3.12`

**License:** MIT License  

> _3x-ui is under development. py3xui also. I am not related with 3x-ui or py3xui. This project is only for educational purposes_

---

## 🚀 Quick Start

### 💾 Installation
```bash
pip install py_multi_3xui
```

---

## ⚙️ Operating with servers

### ➕ Adding server to database
```python
from py_multi_3xui import Server
from py_multi_3xui import ServerDataManager

username = "Ben"
password = "BenLoveApples123"
host = "https://benserver.com:PORT/PATH/"
internet_speed = 5  # amount in gb per second.
location = "usa"
secret_token_for_2FA = "32secretbase32"

server = Server(admin_username=username,
                password=password,
                host=host,
                location=location,
                internet_speed=internet_speed,
                use_tls_verification=True,
                secret_token_for_2FA=secret_token_for_2FA)

data_manager = ServerDataManager()
data_manager.add_server(server)
```

> 💡 Learn your server's traffic speed by using [Ookla](https://www.speedtest.net/) or ask your VPS seller.  
> ⚠ There is no filtration by valid country code. You can add some silly locations to db

---

### ❌ Deleting server from database
```python
from py_multi_3xui import ServerDataManager

host = "some_server.com:PORT/PATH/"
manager = ServerDataManager()
manager.delete_server(host)
```

---

### 🌍 Get best server by country
```python
from py_multi_3xui import ServerDataManager

manager = ServerDataManager()
location = "usa"
best_server = await manager.choose_best_server_by_location(location)
print(best_server)
```

---

## 👥 Working with clients/configs

### 🆕 Generate client (not add)
```python

from py_multi_3xui import RandomStuffGenerator as rsg
from py_multi_3xui import Server
from py3xui import Client

total_gb = 30
inbound_id = 4
limit_ip = 0
client_email = rsg.generate_email(10)
expiry_time = 30
up = 0
down = 0

#note, generate. NOT ADD. This method returns only client instance
client = Server.generate_client(total_gb=total_gb,
                                inbound_id=inbound_id,
                                limit_ip=limit_ip,
                                client_email=client_email,
                                expiry_time=expiry_time,
                                up=up,
                                down=down)
```
> _For more complete info about **py3xui.Client** visit [py3xui documentation](https://github.com/iwatkot/py3xui)._

---

### ➕ Add client to server
```python
from py_multi_3xui import Server
from py3xui import Client

server = ...
client = ...

await server.add_client(client)
```

---

### ✏️ Edit/Update client
```python
from py3xui import Client
from py_multi_3xui import Server

server = ...
client = await server.get_client_by_email("some_email")
client.up = 50
client.down = 30#just edit some client's fields

server.update_client(client)
```

---

### 🔑 Get connection string
```python
from py_multi_3xui import Server
from py3xui import Client
server = ...
client = ...
remark = "MyAwesomeVPN"
port = 443# standard port for VLESS+Reality combo
config = server.get_config(client,remark,port)
```

---

### 🗑 Delete client by uuid
```python
server = ...
uuid = "some uuid"
inbound_id = 4
server.delete_client_by_uuid(client_uuid=uuid, inbound_id=inbound_id)
```

---

## 🐞 Bugs and Features
Please report any bugs or feature requests by opening an issue on [GitHub issues](https://github.com/Dmeetrogon/py_multi_3xui/issues)  
Or DM me via Telegram(through DM to channel): [@dmeetprofile](https://t.me/dmeetprofile)

---

## ❤️ Donate and Support
If this project was helpful for you:  
- ⭐ Star it on GitHub  
- 💰 Donate via [CryptoBot](https://t.me/send?start=IVFCR3tEjcyk)  
- 💎 Ton: `UQCOKDO9dRYNe3Us8FDK2Ctz6B4fhsonaoKpK93bqneFAyJL`

---

## 📌 Plans
- [ ] Add manual
- [ ] Add ability to work not only with VLESS+Reality configs
- [ ] Improve database (add encryption, verification and etc)  









