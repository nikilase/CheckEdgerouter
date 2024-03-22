import pprint
from dataclasses import dataclass


@dataclass
class SshConf:
    HOST: str = "localhost"
    PORT: int = 22
    USER: str = "admin"
    PASSWORD: str = "password"


@dataclass
class InfluxConf:
    HOST: str = "localhost"
    PORT: str = "8086"
    DB: str = "db"
    MSRMT: str = "measurement"
    RET: str = "autogen"
    USER: str = "user"
    PASSWORD: str = "password"
    TZ: str = "Europe/Berlin"
    PREC: str = "s"
    CONS: str = "one"
    SSL: bool = False
    VERIFY_SSL: bool = False
