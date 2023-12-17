from wireguard.linux import Linux
from wireguard.mikrotik import MikroTik
from wireguard.wireguard import WireGuard


class ServerFactory:
    _instance = None
    _created_servers = {}

    def __new__(cls):
        """Create or return the singleton instance of ServerFactory."""
        if cls._instance is None:
            cls._instance = super(ServerFactory, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def create_server_instance(server_name: str, server_data: dict) -> WireGuard:
        """Create an instance of a WireGuard server based on the provided class name and server data.

        Args:
            server_name (str): The name of the server.
            server_data (dict): A dictionary containing server configuration data.

        Returns:
            WireGuard: An instance of the WireGuard server.

        Raises:
            ValueError: If an unknown server class is provided.
        """
        if server_name in ServerFactory._created_servers:
            return ServerFactory._created_servers[server_name]

        server_type = server_data.pop('type')

        if server_type == 'Linux':
            instance = Linux(**server_data)
        elif server_type == 'MikroTik':
            instance = MikroTik(**server_data)
        else:
            raise ValueError(f'Unknown server class: {server_type}')

        ServerFactory._created_servers[server_name] = instance

        return instance
