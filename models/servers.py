from enum import Enum
from typing import Annotated

from pydantic import BaseModel, AnyUrl, IPvAnyAddress, Field, AliasChoices, AliasPath


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

    path_to_config: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            'path_to_config',
            AliasPath('data', 'path_to_config'),
            AliasPath('data', 'config'),
        ),
    )

    interface_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            'interface_name',
            AliasPath('data', 'interface_name'),
            AliasPath('data', 'interface'),
        ),
    )

    endpoint: IPvAnyAddress | AnyUrl | None = Field(
        default=None,
        validation_alias=AliasChoices('endpoint', AliasPath('data', 'endpoint')),
    )

    dns: IPvAnyAddress | None = None

    server: IPvAnyAddress | AnyUrl | None = Field(
        default=None,
        validation_alias=AliasChoices('server', AliasPath('data', 'server')),
    )

    port: Annotated[int, Field(strict=True, ge=1, le=65535)] | None = Field(
        default=None,
        validation_alias=AliasChoices('port', AliasPath('data', 'port')),
    )

    username: str | None = Field(
        default=None,
        validation_alias=AliasChoices('username', AliasPath('data', 'username')),
    )

    password: str | None = Field(
        default=None,
        validation_alias=AliasChoices('password', AliasPath('data', 'password')),
    )

    key_filename: str | None = None
