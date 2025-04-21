from unittest.mock import patch

import pytest

from wg_assistant.config.servers import get_servers
from wg_assistant.models.servers import ServerModel


def test_valid_server_config_loads(valid_server_data, patch_open_with_data):
    with patch_open_with_data(valid_server_data):
        servers = get_servers()
        assert all(isinstance(server, ServerModel) for server in servers)
        assert [server.name for server in servers] == ['server 1', 'server 2']


def test_old_format_migrates_correctly(old_format_server_data, patch_open_with_data):
    with patch_open_with_data(old_format_server_data):
        servers = get_servers()
        assert [server.name for server in servers] == ['server 3', 'server 4']


def test_duplicate_server_names_raises(duplicate_names_server_data, patch_open_with_data):
    with patch_open_with_data(duplicate_names_server_data):
        with pytest.raises(ValueError, match='Duplicate server names detected'):
            get_servers()


def test_missing_file_returns_default():
    with patch('pathlib.Path.open', side_effect=FileNotFoundError()):
        servers = get_servers()
        assert len(servers) == 1
        assert servers[0].name == 'WireGuard'
