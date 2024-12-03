from enum import Enum

from wireguard.client.local import LocalClient
from wireguard.client.remote import RemoteClient
from wireguard.linux import Linux
from wireguard.routeros import RouterOS
from wireguard.wireguard import WireGuard


class ServerType(Enum):
    LINUX = 'Linux'
    ROUTEROS = 'RouterOS'


class ServerFactory:
    _instance = None
    _created_servers = {}

    def __new__(cls):
        """Create or return the singleton instance of ServerFactory."""
        if cls._instance is None:
            cls._instance = super(ServerFactory, cls).__new__(cls)
        return cls._instance

    @classmethod
    def create_server_instance(cls, server_name: str, server_data: dict) -> WireGuard:
        """Create an instance of a WireGuard server based on the provided class name and server data.

        Args:
            server_name (str): The name of the server.
            server_data (dict): A dictionary containing server configuration data.

        Returns:
            WireGuard: An instance of the WireGuard server.

        Raises:
            ValueError: If an unknown server class is provided or if required data is missing.
        """
        # Return existing instance if already created
        if server_name in cls._created_servers:
            return cls._created_servers[server_name]

        # Extract and validate server data
        server_type_str = server_data.get('type')
        data = server_data.get('data')

        if not server_type_str or not data:
            raise ValueError("Invalid server data: 'type' and 'data' are required.")

        try:
            server_type = ServerType(server_type_str)
        except ValueError:
            raise ValueError(f'Unknown server type: {server_type_str}')

        # Backward compatibility: rename keys and set default endpoint
        if 'interface' in data:
            data['interface_name'] = data.pop('interface')
        if 'endpoint' not in data:
            data['endpoint'] = data.get('server')

        # Handle server type
        match server_type:
            case ServerType.LINUX:
                # Backward compatibility: rename 'config' key
                if 'config' in data:
                    data['path_to_config'] = data.pop('config')

                credential_keys = ['server', 'port', 'username', 'password']
                credentials = {key: data.pop(key, None) for key in credential_keys}

                has_no_credentials = any(value is None for value in credentials.values())
                client = LocalClient() if has_no_credentials else RemoteClient(**credentials)

                instance = Linux(**data, client=client)

            case ServerType.ROUTEROS:
                instance = RouterOS(**data)

            case _:
                raise ValueError(f'Unhandled server type: {server_type}')

        # Cache and return the created instance
        cls._created_servers[server_name] = instance
        return instance
