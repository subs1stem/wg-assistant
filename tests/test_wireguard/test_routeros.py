from unittest.mock import MagicMock, patch, call

import pytest
from routeros_api.api import RouterOsApi, RouterOsApiPool

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


def test_get_config():
    pass  # TODO


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


def test_get_peers():
    pass  # TODO


def test_add_peer():
    pass  # TODO


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
