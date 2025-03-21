from dataclasses import dataclass

@dataclass
class Db_config():
    host: str
    user: str
    passwd: str
    database: str



