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

    return [Server(**server) for server in servers_data]
