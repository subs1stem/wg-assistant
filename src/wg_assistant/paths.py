from pathlib import Path


def get_project_root() -> Path:
    current = Path(__file__).resolve()
    while current.name != 'wg-assistant':
        current = current.parent
    return current


PROJECT_ROOT = get_project_root()
DB_PATH = PROJECT_ROOT / 'wg_assistant.db'
SERVERS_FILE = PROJECT_ROOT / 'servers.json'
