import io
from unittest.mock import MagicMock, patch, call

import pytest
from wgconfig import WGConfig

from wg_assistant.wireguard.client.base import BaseClient
from wg_assistant.wireguard.linux import Linux
from wg_assistant.wireguard.protocol.base import BaseProtocol


@pytest.fixture
def mock_client():
    client = MagicMock(spec=BaseClient)
    client.get_file_contents.return_value = '[Interface]\nPrivateKey = privkey\n'
    return client


@pytest.fixture
def mock_protocol():
    protocol = MagicMock(spec=BaseProtocol)
    protocol.get_command.return_value = 'wg'
    protocol.get_quick_command.return_value = 'wg-quick'
    protocol.parse_config_to_dict.return_value = {'Interface': {'PrivateKey': 'privkey'}}
    return protocol


@pytest.fixture
def linux(mock_client, mock_protocol):
    with patch('wg_assistant.wireguard.linux.WGConfig', spec=True):
        linux = Linux(client=mock_client, protocol=mock_protocol)
        return linux


@pytest.fixture
def wg_show_output():
    return (
        'interface: wg0\n'
        '   public key: pubkey\n'
        '   listening port: 51820\n\n'
        'peer: pubkey1\n'
        '   endpoint: 203.0.113.10:4234\n'
        '   allowed ips: 10.0.0.2/32\n'
        '   latest handshake: 1 minute, 2 seconds ago\n\n'
        'peer: pubkey2\n'
        '   endpoint: 203.0.113.11:42574\n'
        '   allowed ips: 10.0.0.3/32\n'
        '   latest handshake: 10 seconds ago\n'
    )


def test_generate_key_pair(mock_client, mock_protocol, linux):
    mock_client.execute.side_effect = [
        (None, io.StringIO('privkey\n'), None),
        (None, io.StringIO('pubkey\n'), None),
    ]

    privkey, pubkey = linux._generate_key_pair()

    assert privkey == 'privkey'
    assert pubkey == 'pubkey'

    mock_client.execute.assert_has_calls([
        call('wg genkey'),
        call('echo "privkey" | wg pubkey'),
    ])


def test_sync_config(mock_client, mock_protocol, linux):
    linux.sync_config()

    mock_protocol.get_command.assert_called_once_with()
    mock_protocol.get_quick_command.assert_called_once_with()
    mock_client.execute.assert_called_once_with(
        'wg syncconf wg0 <(wg-quick strip /etc/wireguard/wg0.conf)'
    )


def test_get_external_ip(mock_client, linux):
    mock_client.execute.return_value = (
        None,
        io.StringIO('1.1.1.1 via 198.51.100.1 dev eth0 src 198.51.100.42 uid 0\n'),
        None,
    )
    result = linux.get_external_ip()
    assert str(result) == '198.51.100.42'


def test_reboot_host(mock_client, linux):
    linux.reboot_host()
    mock_client.execute.assert_called_once_with('reboot')


@pytest.mark.parametrize(
    'as_dict,expected',
    [
        (False, '[Interface]\nPrivateKey = privkey\nAddress = 10.0.0.1/24\n'),
        (True, {'Interface': {'PrivateKey': 'privkey'}}),
    ],
    ids=['raw', 'as dict'],
)
def test_get_config(mock_client, mock_protocol, linux, as_dict, expected):
    mock_client.execute.return_value = (
        None,
        io.StringIO('[Interface]\nPrivateKey = privkey\nAddress = 10.0.0.1/24\n'),
        None,
    )

    config = linux.get_config(as_dict=as_dict)

    assert config == expected

    if as_dict:
        mock_protocol.parse_config_to_dict.assert_called_once()
    else:
        mock_protocol.parse_config_to_dict.assert_not_called()


@pytest.mark.parametrize('is_enabled,command', [(True, 'up'), (False, 'down')], ids=['true', 'false'])
def test_set_wg_enabled(mock_client, linux, is_enabled, command):
    linux.set_wg_enabled(is_enabled)
    mock_client.execute.assert_called_once_with(f'wg-quick {command} wg0')


@pytest.mark.parametrize('is_enabled,stdout', [(True, 'peers'), (False, '')], ids=['true', 'false'])
def test_get_wg_enabled(mock_client, linux, is_enabled, stdout):
    mock_client.execute.return_value = (None, io.StringIO(stdout), None)
    assert linux.get_wg_enabled() == is_enabled
    mock_client.execute.assert_called_once_with('wg show wg0')


@pytest.mark.parametrize(
    'stdout,stderr,pubkey',
    [('pubkey\n', '', 'pubkey'), ('', 'error\n', None)],
    ids=['ok', 'error'],
)
def test_get_server_pubkey(mock_client, linux, stdout, stderr, pubkey):
    mock_client.execute.return_value = (None, io.StringIO(stdout), io.StringIO(stderr))
    assert linux.get_server_pubkey() == pubkey
    mock_client.execute.assert_called_once_with('wg show wg0 public-key')


def test_get_peers_ok(mock_client, linux, wg_show_output, monkeypatch):
    stdout_bytes = wg_show_output.encode('utf-8')
    mock_client.execute.return_value = (None, io.BytesIO(stdout_bytes), io.StringIO(''))

    mock_get_config = MagicMock(return_value={'Rick': {'PublicKey': 'pubkey1'}, 'Daryl': {'PublicKey': 'pubkey2'}})
    monkeypatch.setattr(linux, 'get_config', mock_get_config)

    result = linux.get_peers()

    assert result == {
        'Rick': {
            'endpoint': '203.0.113.10:4234',
            'allowed ips': '10.0.0.2/32',
            'latest handshake': '1 minute, 2 seconds ago',
        },
        'Daryl': {
            'endpoint': '203.0.113.11:42574',
            'allowed ips': '10.0.0.3/32',
            'latest handshake': '10 seconds ago',
        },
    }

    mock_client.execute.assert_called_once_with('wg show wg0')
    mock_get_config.assert_called_once_with(as_dict=True)


def test_get_peers_error(mock_client, linux):
    mock_client.execute.return_value = (None, io.StringIO(''), io.StringIO('error'))
    assert linux.get_peers() == {}


def test_add_peer(mock_client, mock_protocol, linux, monkeypatch):
    monkeypatch.setattr(linux, 'get_config', MagicMock(return_value={'Interface': {'ListenPort': 51820}}))
    monkeypatch.setattr(linux, '_generate_key_pair', MagicMock(return_value=('privkey', 'pubkey')))
    monkeypatch.setattr(linux, 'get_available_ip', MagicMock(return_value='10.0.0.2'))
    monkeypatch.setattr(linux, 'get_server_pubkey', MagicMock(return_value='server_pubkey'))
    monkeypatch.setattr(linux, 'get_external_ip', MagicMock(return_value='203.0.113.5'))

    mock_protocol.add_peer.return_value = linux.wg_config
    mock_protocol.build_client_config.return_value = 'client_config'

    result = linux.add_peer('test_peer')

    assert result == 'client_config'
    mock_protocol.add_peer.assert_called_once_with(linux.wg_config, 'pubkey', 'test_peer')
    linux.wg_config.add_attr.assert_called_once_with('pubkey', 'AllowedIPs', '10.0.0.2')
    mock_protocol.build_client_config.assert_called_once_with(
        privkey='privkey',
        address='10.0.0.2',
        server_pubkey='server_pubkey',
        server_port=51820,
        server_external_ip='203.0.113.5',
        server_config={'Interface': {'ListenPort': 51820}},
    )


def test_delete_peer(mock_client, linux):
    linux.delete_peer('pubkey')
    linux.wg_config.del_peer.assert_called_once_with('pubkey')


@pytest.mark.parametrize('is_enabled', [True, False])
def test_set_peer_enabled(mock_client, linux, is_enabled):
    linux.set_peer_enabled('pubkey', is_enabled)

    if is_enabled:
        linux.wg_config.enable_peer.assert_called_once_with('pubkey')
        linux.wg_config.disable_peer.assert_not_called()
    else:
        linux.wg_config.disable_peer.assert_called_once_with('pubkey')
        linux.wg_config.enable_peer.assert_not_called()


@pytest.mark.parametrize('is_enabled', [True, False])
def test_get_peer_enabled(mock_client, linux, is_enabled):
    linux.wg_config.get_peer_enabled.return_value = is_enabled

    result = linux.get_peer_enabled('pubkey')

    assert result is is_enabled
    linux.wg_config.get_peer_enabled.assert_called_once_with('pubkey')


def test_rename_peer(mock_protocol, linux):
    old_config = linux.wg_config
    new_config = MagicMock(spec=WGConfig)
    mock_protocol.rename_peer.return_value = new_config

    linux.rename_peer('pubkey', 'new_name')

    mock_protocol.rename_peer.assert_called_once_with(old_config, 'pubkey', 'new_name')
    assert linux.wg_config is new_config
