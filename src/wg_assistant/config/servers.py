import json
import logging

from wg_assistant.models.servers import ServerModel
from wg_assistant.paths import SERVERS_FILE


def _migrate_old_format(data: dict) -> list[dict]:
    logging.info('Old server config format detected, applying migration')
    return [{'name': key, **value} for key, value in data.items()]


def _validate_server_names(servers: list[dict]) -> None:
    names = [s.get('name') for s in servers]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate server names detected')


def get_servers() -> list[ServerModel]:
    """Loads server configurations from a JSON file and converts them into a list of Server objects.

    Returns:
        list[Server]: A list of Server objects representing the server configurations.
    """
    try:
        with SERVERS_FILE.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.info('Servers file not found, local WireGuard server will be used')
        return [ServerModel(name='WireGuard')]

    if isinstance(data, dict):
        data = _migrate_old_format(data)

    _validate_server_names(data)

    logging.info(f'{len(data)} servers loaded from {SERVERS_FILE}')
    return [ServerModel(**server) for server in data]
