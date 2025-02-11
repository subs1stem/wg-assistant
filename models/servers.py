from enum import Enum

from pydantic import BaseModel, AnyUrl, IPvAnyAddress, conint


class ServerType(str, Enum):
    LINUX = 'Linux'
    ROUTEROS = 'RouterOS'


class Protocol(str, Enum):
    WIREGUARD = 'WireGuard'
    AMNEZIA_WG = 'AmneziaWG'


class Server(BaseModel):
    name: str
    type: ServerType = ServerType.LINUX
    protocol: Protocol = Protocol.WIREGUARD
    interface_name: str | None = None
    endpoint: IPvAnyAddress | AnyUrl | None = None
    path_to_config: str | None = None
    server: IPvAnyAddress | AnyUrl | None = None
    port: conint(ge=1, le=65535) | None = None
    username: str | None = None
    password: str | None = None
    key_filename: str | None = None
