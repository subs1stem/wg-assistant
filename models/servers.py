from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ServerType(str, Enum):
    LINUX = 'Linux'
    ROUTEROS = 'RouterOS'


class Protocol(str, Enum):
    WIREGUARD = 'WireGuard'
    AMNEZIA_WG = 'AmneziaWG'


class Server(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    type: ServerType = Field(default=ServerType.LINUX, validate_default=True)
    protocol: Protocol = Field(default=Protocol.WIREGUARD, validate_default=True)
    interface_name: str | None = None
    endpoint: str | None = None
    path_to_config: str | None = None
    server: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    key_filename: str | None = None
