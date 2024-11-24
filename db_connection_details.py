from dataclasses import dataclass


@dataclass
class DBConnectionDetails:
    host: str
    port: str
    user: str
    password: str
    database: str