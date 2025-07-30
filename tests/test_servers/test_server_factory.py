from unittest.mock import MagicMock, patch

import pytest

from wg_assistant.models.server import ServerModel, Protocol, ServerType
from wg_assistant.servers.server_factory import ServerFactory
from wg_assistant.wireguard.client.local import LocalClient
from wg_assistant.wireguard.client.remote import RemoteClient
from wg_assistant.wireguard.linux import Linux
from wg_assistant.wireguard.protocol.amnezia_wg import AmneziaWGProtocol
from wg_assistant.wireguard.protocol.wireguard import WireguardProtocol
from wg_assistant.wireguard.routeros import RouterOS
from wg_assistant.wireguard.wireguard import WireGuard


def test_server_factory_singleton():
    ServerFactory._instance = None

    instance1 = ServerFactory()
    assert isinstance(instance1, ServerFactory)

    instance2 = ServerFactory()
    assert instance2 is instance1


@pytest.mark.parametrize(
    'existing_servers,server_name,is_existing',
    [
        ({'test1': MagicMock(spec=WireGuard)}, 'test1', True),
        ({'test1': MagicMock(spec=WireGuard)}, 'new_server', False),
    ],
    ids=['returns existing', 'creates new'],
)
@patch('wg_assistant.servers.server_factory.ServerFactory._get_protocol', autospec=True, return_value='mock_protocol')
@patch(
    'wg_assistant.servers.server_factory.ServerFactory._create_instance',
    autospec=True,
    return_value=MagicMock(spec=WireGuard)
)
def test_create_server_instance(mock_create_instance, mock_get_protocol, existing_servers, server_name, is_existing):
    ServerFactory._created_servers = existing_servers.copy()
    model = ServerModel(name=server_name)

    instance = ServerFactory.create_server_instance(model)

    if is_existing:
        assert instance == existing_servers[server_name]
        mock_get_protocol.assert_not_called()
        mock_create_instance.assert_not_called()
    else:
        mock_get_protocol.assert_called_once_with(model)
        mock_create_instance.assert_called_once_with(model, 'mock_protocol')
        assert ServerFactory._created_servers[server_name] == instance
        assert isinstance(instance, WireGuard)


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
    model.protocol = MagicMock(spec=Protocol, value='fake_protocol')

    with pytest.raises(ValueError, match='Unhandled protocol type: fake_protocol'):
        ServerFactory._get_protocol(model)


@pytest.mark.parametrize(
    'server_model_type,expected_wireguard_class',
    [
        (ServerType.LINUX, Linux),
        (ServerType.ROUTEROS, RouterOS),
    ],
    ids=['linux', 'routeros'],
)
@patch('wg_assistant.servers.server_factory.Linux', autospec=True)
@patch('wg_assistant.servers.server_factory.RouterOS', autospec=True)
@patch(
    'wg_assistant.servers.server_factory.ServerFactory._get_linux_client',
    autospec=True,
    return_value='mock_linux_client',
)
def test_create_instance(
        mock_get_linux_client,
        mock_routeros_class,
        mock_linux_class,
        server_model_type,
        expected_wireguard_class,
):
    protocol = WireguardProtocol()
    protocol_enum = Protocol.WIREGUARD

    model = ServerModel(
        name='test',
        type=server_model_type,
        protocol=protocol_enum,
        path_to_config='/etc/wireguard/wg0.conf',
        interface_name='wg0',
        server='wg.example.com',  # type: ignore
        port=45022,
        username='root',
        password='password',
    )

    result = ServerFactory._create_instance(model, protocol)
    assert isinstance(result, expected_wireguard_class)

    if server_model_type == ServerType.LINUX:
        mock_routeros_class.assert_not_called()
        mock_get_linux_client.assert_called_once_with(model)
        mock_linux_class.assert_called_once_with(
            client='mock_linux_client',
            protocol=protocol,
            interface_name='wg0',
            path_to_config='/etc/wireguard/wg0.conf',
        )
    else:
        mock_linux_class.assert_not_called()
        mock_get_linux_client.assert_not_called()
        mock_routeros_class.assert_called_once_with(
            server='wg.example.com',
            port=45022,
            username='root',
            password='password',
            protocol=protocol,
            interface_name='wg0',
        )


def test_create_instance_unhandled():
    model = ServerModel(name='test')
    model.type = MagicMock(spec=ServerType, value='fake_server')
    protocol = WireguardProtocol()

    with pytest.raises(ValueError, match='Unhandled server type: fake_server'):
        ServerFactory._create_instance(model, protocol)


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
