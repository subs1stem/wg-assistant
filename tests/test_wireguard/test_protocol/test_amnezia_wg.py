from ipaddress import IPv4Address

from wgconfig import WGConfig

from wg_assistant.wireguard.protocol.amnezia_wg import AmneziaWGProtocol


def test_build_client_config_with_server_config():
    protocol = AmneziaWGProtocol(endpoint='10.0.0.1', dns='8.8.8.8')  # type: ignore

    server_config = {
        'Interface': {
            'Jc': 1, 'Jmin': 2, 'Jmax': 3, 'S1': 4, 'S2': 5,
            'H1': 6, 'H2': 7, 'H3': 8, 'H4': 9
        }
    }

    config_str = protocol.build_client_config(
        privkey='privkey',
        address='10.0.0.2/24',
        server_pubkey='pubkey',
        server_port=51820,
        server_external_ip=IPv4Address('203.0.113.5'),
        server_config=server_config,
    )

    assert '[Peer]' in config_str
    assert 'PublicKey = pubkey' in config_str
    assert 'Endpoint = 10.0.0.1:51820' in config_str
    assert 'PrivateKey = privkey' in config_str
    assert 'Address = 10.0.0.2/24' in config_str
    assert 'DNS = 8.8.8.8' in config_str

    for param, value in server_config['Interface'].items():
        assert f'{param} = {value}' in config_str


def test_build_client_config_missing_params_defaults_to_zero():
    protocol = AmneziaWGProtocol(endpoint='10.0.0.1', dns='8.8.8.8')  # type: ignore
    server_config = {'Interface': {}}  # no params given
    config_str = protocol.build_client_config(
        privkey='privkey',
        address='10.0.0.2/24',
        server_pubkey='pubkey',
        server_port=51820,
        server_config=server_config,
    )

    for param in ['Jc', 'Jmin', 'Jmax', 'S1', 'S2', 'H1', 'H2', 'H3', 'H4']:
        assert f'{param} = 0' in config_str


def test_parse_config_to_dict_amneziawg():
    raw_config = (
        '[Interface]\n'
        'PrivateKey = privkey\n'
        'Address = 10.0.0.1/24\n'
        '[Peer]\n'
        'PublicKey = pubkey1\n'
        'AllowedIPs = 10.0.0.0/24\n'
        '[Peer]\n'
        f'{AmneziaWGProtocol.NAME_ATTR} = NamedPeer\n'
        'PublicKey = pubkey2\n'
        'AllowedIPs = 0.0.0.0/0\n'
        '[Peer]\n'
        'PublicKey = pubkey3\n'
        'AllowedIPs = 10.10.10.0/24\n'
    )

    result = AmneziaWGProtocol.parse_config_to_dict(raw_config)

    assert result['Interface']['PrivateKey'] == 'privkey'
    assert result['Interface']['Address'] == '10.0.0.1/24'

    assert result['pubkey1']['PublicKey'] == 'pubkey1'
    assert result['pubkey1']['AllowedIPs'] == '10.0.0.0/24'

    assert result['NamedPeer']['PublicKey'] == 'pubkey2'
    assert result['NamedPeer']['AllowedIPs'] == '0.0.0.0/0'

    assert result['pubkey3']['PublicKey'] == 'pubkey3'
    assert result['pubkey3']['AllowedIPs'] == '10.10.10.0/24'


def test_add_peer_amneziawg():
    wg_config = WGConfig('/tmp/test.conf')
    wg_config.contents = '[Interface]\nAddress = 10.0.0.1/24\n'

    protocol = AmneziaWGProtocol()

    updated = protocol.add_peer(wg_config, 'pubkey', 'TestPeer')
    assert any('TestPeer' in line for line in updated.lines)


def test_rename_peer_enabled():
    wg_config = WGConfig('/tmp/test.conf')

    wg_config.lines = [
        f'{AmneziaWGProtocol.NAME_ATTR} = OldName\n',
        'PublicKey = pubkey\n'
    ]

    wg_config.get_peer_enabled = lambda key: True
    wg_config.get_sectioninfo = lambda key: (-1, 0)

    protocol = AmneziaWGProtocol()

    updated = protocol.rename_peer(wg_config, 'pubkey', 'NewName')
    assert any('NewName' in line for line in updated.lines)


def test_rename_peer_disabled():
    wg_config = WGConfig('/tmp/test.conf')

    wg_config.lines = [
        f'#! {AmneziaWGProtocol.NAME_ATTR} = OldName\n',
        '#! PublicKey = pubkey\n'
    ]

    wg_config.get_peer_enabled = lambda key: False

    protocol = AmneziaWGProtocol()

    updated = protocol.rename_peer(wg_config, 'pubkey', 'NewName')
    assert updated.lines[0].strip() == f'#! {AmneziaWGProtocol.NAME_ATTR} = NewName'


def test_get_commands_amneziawg():
    assert AmneziaWGProtocol.get_command() == 'awg'
    assert AmneziaWGProtocol.get_quick_command() == 'awg-quick'
