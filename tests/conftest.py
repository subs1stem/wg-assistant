import json
from unittest.mock import mock_open, patch

import pytest


@pytest.fixture
def valid_server_data():
    return [
        {'name': 'server 1', 'host': '1.1.1.1'},
        {'name': 'server 2', 'host': 'myserver.com'}
    ]


@pytest.fixture
def old_format_data():
    return {
        'server 3': {'host': 'myserver.old.com'},
        'server 4': {'host': '2.2.2.2'}
    }


@pytest.fixture
def duplicate_names_data():
    return [
        {'name': 'duplicate', 'host': '3.3.3.3'},
        {'name': 'duplicate', 'host': '4.4.4.4'}
    ]


@pytest.fixture
def patch_open_with_data():
    def _patch(data: dict | list):
        return patch('pathlib.Path.open', mock_open(read_data=json.dumps(data)))

    return _patch
