from enum import Enum

from wireguard.client.local import LocalClient
from wireguard.client.remote import RemoteClient
from wireguard.linux import Linux
from wireguard.protocol.amnezia_wg import AmneziaWGProtocol
from wireguard.protocol.base import BaseProtocol
from wireguard.protocol.wireguard import WireguardProtocol
from wireguard.routeros import RouterOS
from wireguard.wireguard import WireGuard


class ServerType(Enum):
    LINUX = 'Linux'
    ROUTEROS = 'RouterOS'


class Protocol(Enum):
    WIREGUARD = 'WireGuard'
    AMNEZIA_WG = 'AmneziaWG'


class ServerFactory:
    _instance = None
    _created_servers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def create_server_instance(cls, server_name: str, server_data: dict) -> WireGuard:
        """Create or retrieve a WireGuard server instance based on the provided server name and configuration.

        Args:
            server_name (str): The name of the server.
            server_data (dict): Configuration data for the server.

        Returns:
            WireGuard: An instance of the WireGuard server.

        Raises:
            ValueError: If required data is missing or the server type is unrecognized.
        """
        if server_name in cls._created_servers:
            return cls._created_servers[server_name]

        server_type = server_data.get('type')
        protocol_type = Protocol(server_data.get('protocol', Protocol.WIREGUARD.value))
        data = server_data.get('data')

        if not server_type or not data:
            raise ValueError("Invalid server data: 'type' and 'data' are required.")

        cls._prepare_data(data)
        protocol = cls._get_protocol(protocol_type)
        instance = cls._create_instance(server_type, data, protocol)

        cls._created_servers[server_name] = instance
        return instance

    @staticmethod
    def _prepare_data(data: dict):
        """Prepare and normalize server data for backward compatibility."""
        if 'interface' in data:
            data['interface_name'] = data.pop('interface')
        if 'endpoint' not in data:
            data['endpoint'] = data.get('server')
        if 'config' in data:
            data['path_to_config'] = data.pop('config')

    @staticmethod
    def _get_protocol(protocol_type: Protocol) -> BaseProtocol:
        """Return the appropriate protocol instance based on the protocol type."""
        match protocol_type:
            case Protocol.WIREGUARD:
                return WireguardProtocol()
            case Protocol.AMNEZIA_WG:
                return AmneziaWGProtocol()
            case _:
                raise ValueError(f'Unhandled protocol type: {protocol_type}')

    @staticmethod
    def _create_instance(server_type: str, data: dict, protocol: BaseProtocol) -> WireGuard:
        """Instantiate and return the appropriate server type."""
        match server_type:
            case ServerType.LINUX.value:
                client = ServerFactory._get_linux_client(data)
                return Linux(**data, client=client, protocol=protocol)

            case ServerType.ROUTEROS.value:
                return RouterOS(**data, protocol=protocol)

            case _:
                raise ValueError(f'Unhandled server type: {server_type}')

    @staticmethod
    def _get_linux_client(data: dict) -> LocalClient | RemoteClient:
        """Determine and return the appropriate client for Linux servers."""
        credential_keys = ['server', 'port', 'username', 'password']
        credentials = {key: data.pop(key, None) for key in credential_keys}

        if any(value is None for value in credentials.values()):
            return LocalClient()

        return RemoteClient(**credentials)
