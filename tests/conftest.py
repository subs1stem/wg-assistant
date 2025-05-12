import json
from unittest.mock import mock_open, patch

import pytest


@pytest.fixture
def valid_server_data():
    return [
        {'name': 'server 1', 'host': '1.1.1.1'},
        {'name': 'server 2', 'host': 'myserver.com'}
    ]


@pytest.fixture
def old_format_server_data():
    return {
        'server 3': {'host': 'myserver.old.com'},
        'server 4': {'host': '2.2.2.2'}
    }


@pytest.fixture
def duplicate_names_server_data():
    return [
        {'name': 'duplicate', 'host': '3.3.3.3'},
        {'name': 'duplicate', 'host': '4.4.4.4'}
    ]


@pytest.fixture
def name_pubkey_peer_list():
    return {
        'Rick': 'uML8vYZpJ4kgq0luCPNC3Rpis8SYuj2+bXhR2nb78Fo=',
        'Daryl': 'SFJZvvuVJscdDoVUSwHJ0vNKDakAnVmhgjASMqCVtGs=',
        'Shane': 'CDKhm4wqrj5OAJuA7yn8SmYsRCsMlC23AmkJXBAGGH4=',
        'Carl': 'GClFQddt6d9PUauk1RVKQ7pMsJOJ94OiLR0no1ao/ns=',
        'Glenn': 'iCR9kDRwKbE/9fMoNFDyboBaH1m6pPoq4Bz+i0wCKmg=',
    }


@pytest.fixture
def server_config_as_dict():
    return {
        'Interface': {
            'PrivateKey': 'ABhm52PSqu5UjymrdH7XjsGtfDEfXk3lbJnsg8e2knY=',
            'ListenPort': '50100',
            'Address': '172.16.0.1/24',
            'PostUp': 'iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE',
            'PostDown': 'iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE'
        },
        'Rick': {
            'PublicKey': 'uML8vYZpJ4kgq0luCPNC3Rpis8SYuj2+bXhR2nb78Fo=',
            'AllowedIPs': '172.16.0.2/32'
        },
        'Daryl': {
            'PublicKey': 'SFJZvvuVJscdDoVUSwHJ0vNKDakAnVmhgjASMqCVtGs=',
            'AllowedIPs': '172.16.0.3/32'
        },
        'Shane': {
            'PublicKey': 'CDKhm4wqrj5OAJuA7yn8SmYsRCsMlC23AmkJXBAGGH4=',
            'AllowedIPs': '172.16.0.4/32'
        },
        'Carl': {
            'PublicKey': 'GClFQddt6d9PUauk1RVKQ7pMsJOJ94OiLR0no1ao/ns=',
            'AllowedIPs': '172.16.0.5/32'
        },
        'Glenn': {
            'PublicKey': 'iCR9kDRwKbE/9fMoNFDyboBaH1m6pPoq4Bz+i0wCKmg=',
            'AllowedIPs': '172.16.0.10/32'
        },
    }


@pytest.fixture
def patch_open_with_data():
    def _patch(data: dict | list):
        return patch('pathlib.Path.open', mock_open(read_data=json.dumps(data)))

    return _patch
