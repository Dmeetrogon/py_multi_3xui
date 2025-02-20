class Server:
    def __init__(self,location:str,host:str,username:str,password:str,internet_speed:int,secret_token:str = None):
        self.__location = location
        self.__host = host
        self.__password = password
        self.__username = username
        self.__secret_token = secret_token
        self.__internet_speed = internet_speed
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
    @staticmethod
    def sqlite_answer_to_instance(answer:tuple):
        return Server(answer[0],answer[1],answer[2],answer[3],answer[4],answer[5])
    def __str__(self):
        return f"{self.host}\n{self.username}\n{self.password}\n{self.secret_token}\n{self.location}\n{self.internet_speed}"