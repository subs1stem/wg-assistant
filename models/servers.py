from enum import Enum
from typing import Annotated, Self, List

from pydantic import BaseModel, IPvAnyAddress, Field, AliasChoices, AliasPath, model_validator, field_validator
from pydantic_extra_types.domain import DomainStr

DEFAULT_INTERFACE_NAME_WIREGUARD = 'wg0'
DEFAULT_INTERFACE_NAME_AMNEZIAWG = 'awg0'
DEFAULT_INTERFACE_NAME_ROUTEROS = 'wireguard1'

DEFAULT_CONFIG_PATH_WIREGUARD = '/etc/wireguard/wg0.conf'
DEFAULT_CONFIG_PATH_AMNEZIAWG = '/etc/amnezia/amneziawg/awg0.conf'

DEFAULT_PORT_SSH = 22
DEFAULT_PORT_ROUTEROS_API = 8728


class ServerType(str, Enum):
    LINUX = 'Linux'
    ROUTEROS = 'RouterOS'


class Protocol(str, Enum):
    WIREGUARD = 'WireGuard'
    AMNEZIA_WG = 'AmneziaWG'


class ServerModel(BaseModel):
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

    endpoint: IPvAnyAddress | DomainStr | None = Field(
        default=None,
        validation_alias=AliasChoices('endpoint', AliasPath('data', 'endpoint')),
    )

    dns: IPvAnyAddress | List[IPvAnyAddress] | None = None

    server: IPvAnyAddress | DomainStr | None = Field(
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

    @field_validator('dns', mode='before')
    def validate_dns(cls, value: str | None) -> str | list[str] | None:
        if value is None:
            return None

        dns_list = [ip.strip() for ip in value.split(',') if ip.strip()]

        if not dns_list:
            return None

        return dns_list[0] if len(dns_list) == 1 else dns_list

    @model_validator(mode='after')
    def set_defaults(self) -> Self:
        if self.path_to_config is None and self.type is ServerType.LINUX:
            match self.protocol:
                case Protocol.WIREGUARD:
                    self.path_to_config = DEFAULT_CONFIG_PATH_WIREGUARD
                case Protocol.AMNEZIA_WG:
                    self.path_to_config = DEFAULT_CONFIG_PATH_AMNEZIAWG

        if self.interface_name is None:
            match self.type:
                case ServerType.LINUX:
                    match self.protocol:
                        case Protocol.WIREGUARD:
                            self.interface_name = DEFAULT_INTERFACE_NAME_WIREGUARD
                        case Protocol.AMNEZIA_WG:
                            self.interface_name = DEFAULT_INTERFACE_NAME_AMNEZIAWG
                case ServerType.ROUTEROS:
                    self.interface_name = DEFAULT_INTERFACE_NAME_ROUTEROS

        if self.port is None and self.server is not None:
            match self.type:
                case ServerType.LINUX:
                    self.port = DEFAULT_PORT_SSH
                case ServerType.ROUTEROS:
                    self.port = DEFAULT_PORT_ROUTEROS_API

        return self
