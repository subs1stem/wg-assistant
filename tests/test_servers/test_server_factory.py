from unittest.mock import MagicMock, patch

import pytest

from wg_assistant.models.server import ServerModel, Protocol
from wg_assistant.servers.server_factory import ServerFactory
from wg_assistant.wireguard.client.local import LocalClient
from wg_assistant.wireguard.client.remote import RemoteClient
from wg_assistant.wireguard.protocol.amnezia_wg import AmneziaWGProtocol
from wg_assistant.wireguard.protocol.wireguard import WireguardProtocol


@pytest.mark.parametrize(
    'protocol_enum,expected_protocol_class',
    [
        (Protocol.WIREGUARD, WireguardProtocol),
        (Protocol.AMNEZIA_WG, AmneziaWGProtocol),
    ],
    ids=['wireguard', 'amnezia_wg'],
)
def test_get_protocol(protocol_enum, expected_protocol_class):
    model = ServerModel(name='test', protocol=protocol_enum)
    result = ServerFactory._get_protocol(model)
    assert isinstance(result, expected_protocol_class)


def test_get_protocol_unhandled():
    model = ServerModel(name='test')
    model.__setattr__('protocol', MagicMock(spec=Protocol, value='fake_protocol'))

    with pytest.raises(ValueError, match='Unhandled protocol type: fake_protocol'):
        ServerFactory._get_protocol(model)


@pytest.mark.parametrize(
    'server,expected_client_class',
    [
        (None, LocalClient),
        ('wg.example.com', RemoteClient),
    ],
    ids=['local', 'remote']
)
@patch('wg_assistant.servers.server_factory.LocalClient', autospec=True)
@patch('wg_assistant.servers.server_factory.RemoteClient', autospec=True)
def test_get_linux_client(mock_remote_client, mock_local_client, server, expected_client_class):
    model = ServerModel(
        name='test',
        server=server,
        port=51820,
        username='root',
        password='admin123',
        key_filename='/path/to/key',
    )

    result = ServerFactory._get_linux_client(model)
    assert isinstance(result, expected_client_class)

    if server is None:
        mock_local_client.assert_called_once_with()
        mock_remote_client.assert_not_called()
    else:
        mock_remote_client.assert_called_once_with(
            server='wg.example.com',
            port=51820,
            username='root',
            password='admin123',
            key_filename='/path/to/key',
        )
        mock_local_client.assert_not_called()
