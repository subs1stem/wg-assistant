from wireguard.linux import Linux

from wireguard.routeros import RouterOS
from wireguard.wireguard import WireGuard


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
        if server_name in cls._created_servers:
            return cls._created_servers[server_name]

        server_type = server_data.get('type')
        connection_data = server_data.get('data')

        if not server_type or not connection_data:
            raise ValueError("Invalid server data. 'type' and 'data' must be provided.")

        # Ensure backward compatibility by renaming old config keys to match constructor parameters
        rename_keys = {
            'interface': 'interface_name',
            'config': 'path_to_config',
        }

        for old_key, new_key in rename_keys.items():
            if old_key in connection_data:
                connection_data[new_key] = connection_data.pop(old_key)

        if server_type == 'Linux':
            instance = Linux(**connection_data)
        elif server_type == 'RouterOS':
            instance = RouterOS(**connection_data)
        else:
            raise ValueError(f'Unknown server class: {server_type}')

        cls._created_servers[server_name] = instance
        return instance
