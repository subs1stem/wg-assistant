from wireguard.linux import Linux
from wireguard.mikrotik import MikroTik
from wireguard.wireguard import WireGuard


class ServerFactory:
    _instance = None
    _created_instances = {}

    def __new__(cls):
        """Create or return the singleton instance of ServerFactory."""
        if cls._instance is None:
            cls._instance = super(ServerFactory, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def create_server_instance(class_name: str, server_name: str, server_data: dict) -> WireGuard:
        """Create an instance of a WireGuard server based on the provided class name and server data.

        Args:
            class_name (str): The name of the server class to create (e.g., "Linux" or "MikroTik").
            server_name (str): The name of the server.
            server_data (dict): A dictionary containing server configuration data.

        Returns:
            WireGuard: An instance of the WireGuard server.

        Raises:
            ValueError: If an unknown server class is provided.
        """
        if server_name in ServerFactory._created_instances:
            return ServerFactory._created_instances[server_name]

        if class_name == 'Linux':
            instance = Linux(**server_data)
        elif class_name == 'MikroTik':
            instance = MikroTik(**server_data)
        else:
            raise ValueError(f'Unknown server class: {class_name}')

        ServerFactory._created_instances[server_name] = instance
        return instance
