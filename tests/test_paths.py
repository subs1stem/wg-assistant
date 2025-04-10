from pathlib import Path
from unittest.mock import patch

from wg_assistant.paths import get_project_root, DB_FILE, SERVERS_FILE


def test_get_project_root_returns_expected_path():
    fake_path = Path('/home/user/projects/wg-assistant/src/wg_assistant/paths.py').resolve()

    with patch('wg_assistant.paths.__file__', str(fake_path)):
        root = get_project_root()
        assert root.name == 'wg-assistant'
        assert root == Path('/home/user/projects/wg-assistant')


def test_db_and_servers_paths_relative_to_root():
    assert DB_FILE.name == 'wg_assistant.db'
    assert SERVERS_FILE.name == 'servers.json'
    assert DB_FILE.parent == SERVERS_FILE.parent == get_project_root()
