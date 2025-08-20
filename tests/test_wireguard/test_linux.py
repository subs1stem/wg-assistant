import io
from unittest.mock import MagicMock, patch, call

import pytest

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


def _wg_show_output(interface='wg0'):  # TODO: check
    return (
        f'interface: {interface}\n'
        '  public key: serverpub\n'
        '  listening port: 51820\n'
        '\n'
        'peer: pkA\n'
        '  endpoint: 203.0.113.10:51820\n'
        '  allowed ips: 10.0.0.2/32\n'
        '  latest handshake: 1 minute, 2 seconds ago\n'
        '\n'
        'peer: pkB\n'
        '  endpoint: 203.0.113.11:51820\n'
        '  allowed ips: 10.0.0.3/32\n'
        '  latest handshake: 10 seconds ago\n'
    )


def test_get_peers_returns_empty_on_stderr(mock_client, mock_protocol, linux):  # TODO: check
    mock_client.execute.return_value = (0, io.StringIO(''), io.StringIO('fatal\n'))
    assert linux.get_peers() == {}


def test_get_peers_parses_bytes_and_maps_names(mock_client, mock_protocol, linux, monkeypatch):  # TODO: check
    stderr = io.StringIO('')
    stdout_bytes = _wg_show_output().encode('utf-8')
    mock_client.execute.return_value = (0, io.BytesIO(stdout_bytes), stderr)

    def fake_get_config(as_dict=False):
        assert as_dict is True
        return {
            'Interface': {'ListenPort': 51820},
            'Alice': {'PublicKey': 'pkA'},
            'Bob': {'PublicKey': 'pkB'},
        }

    monkeypatch.setattr(linux, 'get_config', fake_get_config)

    peers = linux.get_peers()

    assert 'Alice' in peers and 'Bob' in peers
    assert peers['Alice']['endpoint'] == '203.0.113.10:51820'
    assert peers['Bob']['allowed ips'] == '10.0.0.3/32'


def test_add_peer_flow_writes_and_syncs(mock_client, mock_protocol, linux, monkeypatch):  # TODO: check
    linux.wg_config.read_from_fileobj = MagicMock()
    linux.wg_config.write_to_fileobj = MagicMock()

    monkeypatch.setattr(linux, '_generate_key_pair', MagicMock(return_value=('priv', 'pub')))
    monkeypatch.setattr(linux, 'get_available_ip', MagicMock(return_value='10.0.0.2/24'))
    monkeypatch.setattr(linux, 'get_server_pubkey', MagicMock(return_value='serverpub'))
    monkeypatch.setattr(linux, 'get_external_ip', MagicMock(return_value='203.0.113.5'))

    def fake_get_config(as_dict=False):
        assert as_dict is True
        return {'Interface': {'ListenPort': 51820}}

    monkeypatch.setattr(linux, 'get_config', fake_get_config)

    mock_protocol.add_peer.return_value = linux.wg_config
    mock_protocol.build_client_config.return_value = 'CLIENT-CONFIG'

    result = linux.add_peer('TestPeer')
    assert result == 'CLIENT-CONFIG'

    mock_client.get_file_contents.assert_called_once_with(linux.path_to_config)
    assert linux.wg_config.read_from_fileobj.call_count == 1

    linux.wg_config.add_attr.assert_any_call('pub', 'AllowedIPs', '10.0.0.2/24')

    assert linux.wg_config.write_to_fileobj.call_count == 1
    mock_client.put_file_contents.assert_called_once()

    with patch.object(linux, 'sync_config') as sync_mock:
        linux.add_peer('TestPeer2')
        sync_mock.assert_called_once()


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


def test_rename_peer(mock_protocol, linux):  # TODO: check
    mock_protocol.rename_peer.return_value = linux.wg_config
    linux.rename_peer('pubkey', 'new_name')
    mock_protocol.rename_peer.assert_called_once_with(linux.wg_config, 'pubkey', 'new_name')
