import json
import os
from pathlib import Path
from typing import List

from models.servers import Server


def load_servers_from_file(filename: str = 'servers.json') -> List[Server]:
    """Loads server configurations from a JSON file and converts them into a list of Server objects.

    Args:
        filename (str): The name of the JSON file containing the server configurations (defaults to 'servers.json').

    Returns:
        List[Server]: A list of Server objects representing the server configurations.
    """
    file_path = Path(os.getcwd()) / filename

    with file_path.open('r', encoding='utf-8') as f:
        servers_data = json.load(f)

    # Convert old configuration file to new one for backward compatibility
    if type(servers_data) is dict:
        servers_data = [{'name': key, **value} for key, value in servers_data.items()]

    # Check server name uniqueness
    names = [server['name'] for server in servers_data]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate server names detected')

    return [Server(**server) for server in servers_data]
