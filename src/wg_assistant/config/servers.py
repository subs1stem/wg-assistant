import json
import logging
from pathlib import Path

from wg_assistant.models.servers import ServerModel


def _migrate_old_format(data: dict) -> list[dict]:
    logging.info('Old server config format detected, applying migration')
    return [{'name': key, **value} for key, value in data.items()]


def _validate_server_names(servers: list[dict]) -> None:
    names = [s.get('name') for s in servers]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate server names detected')


def get_servers(filename: str = 'servers.json') -> list[ServerModel]:
    """Loads server configurations from a JSON file and converts them into a list of Server objects.

    Args:
        filename (str): The name of the JSON file containing the server configurations (defaults to 'servers.json').

    Returns:
        list[Server]: A list of Server objects representing the server configurations.
    """
    path = Path(__file__).resolve().parents[3] / filename

    try:
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.info('Servers file not found, local WireGuard server will be used')
        return [ServerModel(name='WireGuard')]

    if isinstance(data, dict):
        data = _migrate_old_format(data)

    _validate_server_names(data)

    logging.info(f'{len(data)} servers loaded from {filename}')
    return [ServerModel(**server) for server in data]
