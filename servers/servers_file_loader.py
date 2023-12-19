import json
import os


def load_servers_from_file(filename: str = 'servers.json') -> dict:
    """Load server configurations from a JSON file.

    Args:
        filename (str): The name of the JSON file containing server configurations.
                        Defaults to 'servers.json'.

    Returns:
        dict: A dictionary containing server configurations.
    """
    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path) as f:
        servers = json.load(f)

    return servers
