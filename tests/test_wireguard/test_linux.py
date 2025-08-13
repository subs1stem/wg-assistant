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


def test_get_external_ip_parses_ipv4(mock_client, linux):
    mock_client.execute.return_value = (
        0,
        io.StringIO('1.1.1.1 via 198.51.100.1 dev eth0 src 192.0.2.10 uid 0\n'),
        io.StringIO('')
    )
    result = linux.get_external_ip()
    assert str(result) == '192.0.2.10'


def test_reboot_host_calls_execute(mock_client, linux):
    linux.reboot_host()
    mock_client.execute.assert_called_once_with('reboot')


def test_get_config_as_str(mock_client, linux):
    mock_client.execute.return_value = (
        0,
        io.StringIO('[Interface]\nPrivateKey = abc\nAddress = 10.0.0.1/24\n'),
        io.StringIO('')
    )
    cfg = linux.get_config(as_dict=False)
    assert cfg == '[Interface]\nPrivateKey = abc\nAddress = 10.0.0.1/24\n'


def test_get_config_as_dict(mock_client, mock_protocol, linux):
    mock_client.execute.return_value = (
        0,
        io.StringIO('[Interface]\nPrivateKey = privkey\n'),
        io.StringIO('')
    )
    res = linux.get_config(as_dict=True)
    assert res == {'Interface': {'PrivateKey': 'privkey'}}
    mock_protocol.parse_config_to_dict.assert_called_once()


def test_set_wg_enabled_up(mock_client, mock_protocol, linux):
    linux.set_wg_enabled(True)
    mock_client.execute.assert_called_once_with(
        f'{mock_protocol.get_quick_command()} up {linux.interface_name}'
    )


def test_set_wg_enabled_down(mock_client, mock_protocol, linux):
    linux.set_wg_enabled(False)
    mock_client.execute.assert_called_once_with(
        f'{mock_protocol.get_quick_command()} down {linux.interface_name}'
    )


def test_get_wg_enabled_true(mock_client, mock_protocol, linux):
    mock_client.execute.return_value = (0, io.StringIO('something\n'), io.StringIO(''))
    assert linux.get_wg_enabled() is True
    mock_client.execute.assert_called_once_with(
        f'{mock_protocol.get_command()} show {linux.interface_name}'
    )


def test_get_wg_enabled_false(mock_client, mock_protocol, linux):
    mock_client.execute.return_value = (0, io.StringIO(''), io.StringIO(''))
    assert linux.get_wg_enabled() is False


def test_get_server_pubkey_ok(mock_client, mock_protocol, linux):
    mock_client.execute.return_value = (0, io.StringIO('pubkey123\n'), io.StringIO(''))
    assert linux.get_server_pubkey() == 'pubkey123'
    mock_client.execute.assert_called_once_with(
        f'{mock_protocol.get_command()} show {linux.interface_name} public-key'
    )


def test_get_server_pubkey_none_on_stderr(mock_client, mock_protocol, linux):
    mock_client.execute.return_value = (0, io.StringIO('ignored\n'), io.StringIO('error\n'))
    assert linux.get_server_pubkey() is None


def _wg_show_output(interface='wg0'):
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


def test_get_peers_returns_empty_on_stderr(mock_client, mock_protocol, linux):
    mock_client.execute.return_value = (0, io.StringIO(''), io.StringIO('fatal\n'))
    assert linux.get_peers() == {}


def test_get_peers_parses_bytes_and_maps_names(mock_client, mock_protocol, linux, monkeypatch):
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


def test_add_peer_flow_writes_and_syncs(mock_client, mock_protocol, linux, monkeypatch):
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


def test_delete_peer_writes_and_syncs(mock_client, linux):
    linux.wg_config.read_from_fileobj = MagicMock()
    linux.wg_config.write_to_fileobj = MagicMock()

    linux.delete_peer('pkX')

    mock_client.get_file_contents.assert_called_once_with(linux.path_to_config)
    linux.wg_config.del_peer.assert_called_once_with('pkX')
    mock_client.put_file_contents.assert_called_once()


def test_set_peer_enabled_true_and_false(mock_client, linux):
    linux.wg_config.read_from_fileobj = MagicMock()
    linux.wg_config.write_to_fileobj = MagicMock()

    linux.set_peer_enabled('pkY', True)
    linux.set_peer_enabled('pkY', False)

    assert mock_client.get_file_contents.call_count == 2
    linux.wg_config.enable_peer.assert_called_once_with('pkY')
    linux.wg_config.disable_peer.assert_called_once_with('pkY')
    assert mock_client.put_file_contents.call_count == 2


def test_get_peer_enabled_read_only(mock_client, linux):
    linux.wg_config.read_from_fileobj = MagicMock()
    linux.wg_config.get_peer_enabled.return_value = True

    result = linux.get_peer_enabled('pkZ')
    assert result is True

    mock_client.get_file_contents.assert_called_once_with(linux.path_to_config)
    mock_client.put_file_contents.assert_not_called()


def test_rename_peer_writes_and_syncs(mock_client, mock_protocol, linux):
    linux.wg_config.read_from_fileobj = MagicMock()
    linux.wg_config.write_to_fileobj = MagicMock()

    mock_protocol.rename_peer.return_value = linux.wg_config

    linux.rename_peer('pkR', 'NewName')

    mock_client.get_file_contents.assert_called_once_with(linux.path_to_config)
    mock_protocol.rename_peer.assert_called_once()
    mock_client.put_file_contents.assert_called_once()
