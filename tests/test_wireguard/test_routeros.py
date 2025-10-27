from unittest.mock import MagicMock, patch, call

import pytest
from routeros_api.api import RouterOsApi, RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

from wg_assistant.wireguard.protocol.base import BaseProtocol
from wg_assistant.wireguard.routeros import RouterOS


@pytest.fixture
def mock_api():
    return MagicMock(spec=RouterOsApi)


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


def test_exception_handler_success(routeros):
    fn = MagicMock(return_value='ok')
    wrapped = RouterOS._exception_handler(fn)
    routeros.connect = MagicMock()

    result = wrapped(routeros)

    assert result == 'ok'
    routeros.connect.assert_not_called()


def test_exception_handler_retries_on_connection_error(routeros):
    fn = MagicMock(side_effect=[RouterOsApiConnectionError('boom'), 'ok'])
    wrapped = RouterOS._exception_handler(fn)
    routeros.connect = MagicMock()

    with patch('logging.warning') as mock_warning:
        result = wrapped(routeros)

    assert result == 'ok'
    assert fn.call_count == 2
    routeros.connect.assert_called_once()
    mock_warning.assert_called_once_with('RouterOS API connection error, reconnecting...')
    assert 'reconnecting' in mock_warning.call_args[0][0]


def test_exception_handler_logs_other_exceptions_and_returns_none(routeros, monkeypatch):
    fn = MagicMock(side_effect=Exception('fatal'))
    wrapped = RouterOS._exception_handler(fn)
    routeros.connect = MagicMock()

    with patch('logging.exception') as mock_exception:
        result = wrapped(routeros)

    assert result is None
    routeros.connect.assert_not_called()
    mock_exception.assert_called_once_with('An unexpected error occurred: fatal')
    assert 'unexpected error' in mock_exception.call_args[0][0]


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
    mock_api.get_resource.assert_called_once_with('/interface/wireguard')
    mock_api.get_resource.return_value.get.assert_called_once_with(name='wireguard1')


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
    mock_api.get_resource.assert_called_once_with('/interface/wireguard/peers')
    mock_api.get_resource.return_value.get.assert_called_once_with(public_key='pubkey')


@patch('wg_assistant.wireguard.routeros.RouterOsApiPool')
@pytest.mark.parametrize(
    'side_effect,should_raise,expected_message',
    [
        (None, False, None),
        (RouterOsApiConnectionError('boom'), True, 'Error connecting to RouterOS API: boom'),
    ],
    ids=['success', 'connection error'],
)
def test_connect(mock_routeros_api_pool, routeros, side_effect, should_raise, expected_message):
    mock_connection = MagicMock()
    mock_routeros_api_pool.return_value = mock_connection
    mock_connection.get_api.side_effect = side_effect

    if should_raise:
        with pytest.raises(ConnectionError, match=expected_message):
            routeros.connect()
    else:
        routeros.connect()
        mock_connection.get_api.assert_called_once_with()
        assert routeros.api == mock_connection.get_api.return_value

    mock_routeros_api_pool.assert_called_once_with(
        host=routeros.server,
        username=routeros.username,
        password=routeros.password,
        port=routeros.port,
        plaintext_login=True,
    )
    mock_connection.set_timeout.assert_called_once_with(5)


@pytest.mark.parametrize(
    'route,ip,expected',
    [
        ([{'immediate-gw': '1.2.3.4%ether1'}], [{'address': '1.2.3.4/24'}], '1.2.3.4'),
        ([{'immediate-gw': 'fe80::1%ether1'}], [{'address': 'fe80::1/64'}], 'fe80::1'),
    ],
    ids=['ipv4', 'ipv6'],
)
def test_get_external_ip(routeros, mock_api, route, ip, expected):
    mock_api.get_resource.return_value.get.side_effect = [route, ip]
    result = routeros.get_external_ip()

    assert str(result) == expected

    mock_api.get_resource.return_value.get.assert_has_calls([
        call(dst_address='0.0.0.0/0'),
        call(interface='ether1'),
    ])


def test_reboot_host(routeros, mock_api):
    routeros.reboot_host()

    mock_api.get_binary_resource.assert_called_once_with('/')
    mock_api.get_binary_resource.return_value.call.assert_called_once_with('system/reboot')


@pytest.mark.parametrize('as_dict', [True, False], ids=['as dict', 'as string'])
def test_get_config(routeros, mock_api, as_dict):
    routeros._get_interface = MagicMock(return_value={'private-key': 'privkey', 'listen-port': 12345})
    routeros._format_config_as_string = MagicMock(return_value='config_as_string')

    mock_api.get_resource.return_value.get.side_effect = [
        [
            {'address': '1.2.3.4'}
        ],
        [
            {'name': 'Rick', 'public-key': 'pubkey1', 'allowed-address': '172.16.2.2/32'},
            {'name': 'Daryl', 'public-key': 'pubkey2', 'allowed-address': '172.16.2.3/32'},
        ],
    ]

    expected_config = {
        'Interface': {
            'PrivateKey': 'privkey',
            'ListenPort': 12345,
            'Address': '1.2.3.4',
        },
        'Rick': {
            'PublicKey': 'pubkey1',
            'AllowedIPs': '172.16.2.2/32',
        },
        'Daryl': {
            'PublicKey': 'pubkey2',
            'AllowedIPs': '172.16.2.3/32',
        }
    }

    result = routeros.get_config(as_dict)

    mock_api.get_resource.assert_has_calls([
        call('/ip/address'),
        call().get(interface='wireguard1'),
        call('/interface/wireguard/peers'),
        call().get(interface='wireguard1'),
    ])

    expected = expected_config if as_dict else 'config_as_string'
    assert result == expected

    if as_dict:
        routeros._format_config_as_string.assert_not_called()
    else:
        routeros._format_config_as_string.assert_called_once_with(expected_config)


@pytest.mark.parametrize('interface', [{'id': 123}, None], ids=['interface exists', 'interface missing'])
@pytest.mark.parametrize('is_enabled,disabled', [(True, 'no'), (False, 'yes')], ids=['true', 'false'])
def test_set_wg_enabled(routeros, mock_api, is_enabled, disabled, interface):
    routeros._get_interface = MagicMock(return_value=interface)

    routeros.set_wg_enabled(is_enabled)

    if interface:
        mock_api.get_resource.assert_called_once_with('/interface/wireguard')
        mock_api.get_resource.return_value.set.assert_called_once_with(id=123, disabled=disabled)
    else:
        mock_api.get_resource.assert_not_called()
        mock_api.get_resource.return_value.set.assert_not_called()


@pytest.mark.parametrize(
    'interface,expected',
    [
        ({'disabled': 'false'}, True),
        ({'disabled': 'true'}, False),
        ({}, False),
        (None, False),
    ],
    ids=['interface enabled', 'interface disabled', 'param missing', 'interface missing'],
)
def test_get_wg_enabled(routeros, interface, expected):
    routeros._get_interface = MagicMock(return_value=interface)
    result = routeros.get_wg_enabled()
    assert result == expected


@pytest.mark.parametrize(
    'interface,expected',
    [
        ({'public-key': 'pubkey'}, 'pubkey'),
        ({}, None),
        (None, None),
    ],
    ids=['pubkey exists', 'pubkey missing', 'interface missing'],
)
def test_get_server_pubkey(routeros, interface, expected):
    routeros._get_interface = MagicMock(return_value=interface)
    result = routeros.get_server_pubkey()
    assert result == expected


def test_get_peers(routeros, mock_api):
    mock_api.get_resource.return_value.get.return_value = [
        {
            'name': 'Rick',
            'current-endpoint-address': '1.2.3.4',
            'current-endpoint-port': '43276',
            'allowed-address': '172.16.2.3/32',
            'last-handshake': '1d3h12m46s',
            'rx': '1279682488',
            'tx': '562232384',
        },
        {
            'name': 'Daryl',
        },
    ]

    result = routeros.get_peers()

    assert result == {
        'Rick': {
            'endpoint': '1.2.3.4:43276',
            'allowed ips': '172.16.2.3/32',
            'latest handshake': '1d3h12m46s',
            'transfer': '1.2 GiB , 536.2 MiB',
        },
        'Daryl': {
            'endpoint': 'None:None',
            'allowed ips': None,
            'latest handshake': None,
            'transfer': '0 Bytes , 0 Bytes',
        },
    }

    mock_api.get_resource.assert_called_once_with('/interface/wireguard/peers')
    mock_api.get_resource.return_value.get.assert_called_once_with(interface='wireguard1')


def test_add_peer(routeros):
    routeros.get_config = MagicMock(return_value={'dummy': 'config'})
    routeros._get_interface = MagicMock(return_value={'listen-port': 51820})
    routeros.get_available_ip = MagicMock(return_value='172.16.0.2/32')
    routeros.get_server_pubkey = MagicMock(return_value='pubkey')
    routeros.get_external_ip = MagicMock(return_value='1.2.3.4')

    mock_peers = MagicMock()
    mock_peers.get.return_value = [{
        'private-key': 'privkey',
        'allowed-address': '172.16.0.2/32',
    }]
    mock_api = MagicMock()
    mock_api.get_resource.return_value = mock_peers
    routeros.api = mock_api

    expected_result = 'client_config'
    routeros.protocol.build_client_config = MagicMock(return_value=expected_result)

    result = routeros.add_peer('test_peer')

    assert result == expected_result

    routeros.get_config.assert_called_once_with(as_dict=True)
    routeros._get_interface.assert_called_once()
    routeros.get_available_ip.assert_called_once_with({'dummy': 'config'})

    mock_api.get_resource.assert_called_once_with('/interface/wireguard/peers')
    mock_peers.add.assert_called_once_with(
        name='test_peer',
        interface=routeros.interface_name,
        private_key='auto',
        allowed_address='172.16.0.2/32',
    )
    mock_peers.get.assert_called_once_with(name='test_peer')

    routeros.protocol.build_client_config.assert_called_once_with(
        privkey='privkey',
        address='172.16.0.2/32',
        server_pubkey='pubkey',
        server_port=51820,
        server_external_ip='1.2.3.4',
        server_config={'dummy': 'config'},
    )


@pytest.mark.parametrize('peer', [{'id': 123}, None], ids=['peer exists', 'peer missing'])
def test_delete_peer(routeros, mock_api, peer):
    routeros._get_peer = MagicMock(return_value=peer)
    routeros.delete_peer('pubkey')
    routeros._get_peer.assert_called_once_with('pubkey')

    if peer:
        mock_api.get_resource.assert_called_once_with('/interface/wireguard/peers')
        mock_api.get_resource.return_value.remove.assert_called_once_with(id=123)
    else:
        mock_api.get_resource.assert_not_called()
        mock_api.get_resource.return_value.remove.assert_not_called()


@pytest.mark.parametrize('peer', [{'id': 123}, None], ids=['peer exists', 'peer missing'])
@pytest.mark.parametrize('is_enabled,disabled', [(True, 'no'), (False, 'yes')], ids=['true', 'false'])
def test_set_peer_enabled(routeros, mock_api, is_enabled, disabled, peer):
    routeros._get_peer = MagicMock(return_value=peer)
    routeros.set_peer_enabled('pubkey', is_enabled)
    routeros._get_peer.assert_called_once_with('pubkey')

    if peer:
        mock_api.get_resource.assert_called_once_with('/interface/wireguard/peers')
        mock_api.get_resource.return_value.set.assert_called_once_with(id=123, disabled=disabled)
    else:
        mock_api.get_resource.assert_not_called()
        mock_api.get_resource.return_value.set.assert_not_called()


@pytest.mark.parametrize(
    'peer,expected',
    [
        ({'disabled': 'false'}, True),
        ({'disabled': 'true'}, False),
        ({}, False),
        (None, False),
    ],
    ids=['peer enabled', 'peer disabled', 'param missing', 'peer missing'],
)
def test_get_peer_enabled(routeros, peer, expected):
    routeros._get_peer = MagicMock(return_value=peer)
    result = routeros.get_peer_enabled('pubkey')
    assert result == expected


@pytest.mark.parametrize('peer', [{'id': 123}, None], ids=['peer exists', 'peer missing'])
def test_rename_peer(routeros, mock_api, peer):
    routeros._get_peer = MagicMock(return_value=peer)
    routeros.rename_peer('pubkey', 'new_name')
    routeros._get_peer.assert_called_once_with('pubkey')

    if peer:
        mock_api.get_resource.assert_called_once_with('/interface/wireguard/peers')
        mock_api.get_resource.return_value.set.assert_called_once_with(id=123, name='new_name')
    else:
        mock_api.get_resource.assert_not_called()
        mock_api.get_resource.return_value.set.assert_not_called()
