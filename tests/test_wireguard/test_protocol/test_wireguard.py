from ipaddress import IPv4Address

from wgconfig import WGConfig

from wg_assistant.wireguard.protocol.wireguard import WireguardProtocol


def test_build_client_config_with_defaults():
    protocol = WireguardProtocol(endpoint='10.0.0.1', dns='8.8.8.8')  # type: ignore
    config_str = protocol.build_client_config(
        privkey='privkey',
        address='10.0.0.2/24',
        server_pubkey='pubkey',
        server_port=51820,
        server_external_ip=IPv4Address('203.0.113.5'),
    )

    assert '[Peer]' in config_str
    assert 'PublicKey = pubkey' in config_str
    assert 'Endpoint = 10.0.0.1:51820' in config_str
    assert 'PrivateKey = privkey' in config_str
    assert 'Address = 10.0.0.2/24' in config_str
    assert 'DNS = 8.8.8.8' in config_str


def test_build_client_config_uses_server_config_dns():
    protocol = WireguardProtocol()
    server_config = {'Interface': {'Address': '192.168.0.1/24'}}
    config_str = protocol.build_client_config(
        privkey='privkey',
        address='10.0.0.2/24',
        server_pubkey='pubkey',
        server_port=51820,
        server_external_ip=IPv4Address('203.0.113.5'),
        server_config=server_config,
    )

    assert 'DNS = 192.168.0.1' in config_str


def test_build_client_config_with_list_dns():
    protocol = WireguardProtocol(dns=['8.8.8.8', '1.1.1.1'])  # type: ignore
    config_str = protocol.build_client_config(
        privkey='privkey',
        address='10.0.0.2/24',
        server_pubkey='pubkey',
        server_port=51820,
        server_external_ip=IPv4Address('203.0.113.5'),
    )

    assert 'DNS = 8.8.8.8, 1.1.1.1' in config_str


def test_parse_config_to_dict():
    raw_config = (
        '# Interface\n'
        'PrivateKey = privkey\n'
        'Address = 10.0.0.2/24\n'
        '# Peer\n'
        'PublicKey = pubkey\n'
        'AllowedIPs = 0.0.0.0/0\n'
    )

    result = WireguardProtocol.parse_config_to_dict(raw_config)

    assert result['Interface']['PrivateKey'] == 'privkey'
    assert result['Interface']['Address'] == '10.0.0.2/24'
    assert result['Peer']['PublicKey'] == 'pubkey'
    assert result['Peer']['AllowedIPs'] == '0.0.0.0/0'


def test_add_peer():
    wg_config = WGConfig('/tmp/test.conf')
    wg_config.contents = '[Interface]\nAddress = 10.0.0.1/24\n'
    protocol = WireguardProtocol()

    updated = protocol.add_peer(wg_config, 'pubkey', 'TestPeer')
    assert any('TestPeer' in line for line in updated.lines)


def test_rename_peer_simple_comment():
    wg_config = WGConfig('/tmp/test.conf')
    wg_config.lines = [
        '# OldName\n',
        'PublicKey = pubkey123\n'
    ]
    wg_config.get_sectioninfo = lambda key: (0, 2)
    protocol = WireguardProtocol()

    updated = protocol.rename_peer(wg_config, 'pubkey', 'NewName')
    assert updated.lines[0].strip() == '# NewName'


def test_rename_peer_with_hash_bang_comment():
    wg_config = WGConfig('/tmp/test.conf')
    wg_config.lines = [
        '#! # OldName\n',
        'PublicKey = pubkey123\n'
    ]
    wg_config.get_sectioninfo = lambda key: (0, 2)
    protocol = WireguardProtocol()

    updated = protocol.rename_peer(wg_config, 'pubkey', 'NewName')
    assert updated.lines[0].strip() == '#! # NewName'


def test_get_commands():
    assert WireguardProtocol.get_command() == 'wg'
    assert WireguardProtocol.get_quick_command() == 'wg-quick'
