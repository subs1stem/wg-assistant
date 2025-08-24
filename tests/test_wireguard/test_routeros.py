from unittest.mock import MagicMock, patch

import pytest
from routeros_api.api import RouterOsApi, RouterOsApiPool

from wg_assistant.wireguard.protocol.base import BaseProtocol
from wg_assistant.wireguard.routeros import RouterOS


@pytest.fixture
def mock_api():
    api = MagicMock(spec=RouterOsApi)
    api.get_resource.return_value.get.return_value = []
    return api


@pytest.fixture
def routeros(mock_api):
    with patch('wg_assistant.wireguard.routeros.RouterOsApiPool') as routeros_api:
        connection = MagicMock(spec=RouterOsApiPool)
        connection.get_api.return_value = mock_api
        routeros_api.return_value = connection

        routeros = RouterOS(
            server='127.0.0.1',
            port=8728,
            username='admin',
            password='password',
            protocol=MagicMock(spec=BaseProtocol),
        )

        return routeros


def test_format_config_as_string():
    config = {
        'Interface': {'PrivateKey': 'privkey', 'Address': '10.0.0.1/24'},
        'Peer': {'PublicKey': 'pubkey', 'AllowedIPs': '10.0.0.2/32'},
    }

    result = RouterOS._format_config_as_string(config)

    assert result == (
        '[Interface]\n'
        'PrivateKey = privkey\n'
        'Address = 10.0.0.1/24\n\n'
        '# Peer\n'
        '[Peer]\n'
        'PublicKey = pubkey\n'
        'AllowedIPs = 10.0.0.2/32\n'
    )


@pytest.mark.parametrize(
    'mock_return,expected',
    [
        ([{'id': 1}], {'id': 1}),
        ([], None),
    ],
    ids=['interface exists', 'interface missing'],
)
def test_get_interface(routeros, mock_api, mock_return, expected):
    mock_api.get_resource.return_value.get.return_value = mock_return
    result = routeros._get_interface()
    assert result == expected


@pytest.mark.parametrize(
    'mock_return,expected',
    [
        ([{'id': 1}], {'id': 1}),
        ([], None),
    ],
    ids=['peer exists', 'peer missing'],
)
def test_get_peer(routeros, mock_api, mock_return, expected):
    mock_api.get_resource.return_value.get.return_value = mock_return
    result = routeros._get_peer('pubkey')
    assert result == expected
