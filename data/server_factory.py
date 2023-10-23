from wireguard.linux import Linux
from wireguard.mikrotik import MikroTik
from wireguard.wireguard import WireGuard


def create_server_instance(class_name: str, server_data: dict) -> WireGuard:
    """Create an instance of a WireGuard server based on the provided class name and server data.

    Args:
        class_name (str): The name of the server class to create (e.g., "Linux" or "MikroTik").
        server_data (dict): A dictionary containing server configuration data.

    Returns:
        WireGuard: An instance of the WireGuard server.

    Raises:
        ValueError: If an unknown server class is provided.
    """
    if class_name == 'Linux':
        return Linux(**server_data)
    elif class_name == 'MikroTik':
        return MikroTik(**server_data)
    else:
        raise ValueError(f'Unknown server class: {class_name}')
