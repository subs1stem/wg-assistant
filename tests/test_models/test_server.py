from ipaddress import IPv4Address

import pytest
from pydantic import ValidationError

from wg_assistant.models.server import *


def test_defaults_for_linux_wireguard():
    model = ServerModel(name='test', type=ServerType.LINUX, protocol=Protocol.WIREGUARD)
    assert model.interface_name == DEFAULT_INTERFACE_NAME_WIREGUARD
    assert model.path_to_config == DEFAULT_CONFIG_PATH_WIREGUARD


def test_defaults_for_linux_amnezia():
    model = ServerModel(name='test', type=ServerType.LINUX, protocol=Protocol.AMNEZIA_WG)
    assert model.interface_name == DEFAULT_INTERFACE_NAME_AMNEZIAWG
    assert model.path_to_config == DEFAULT_CONFIG_PATH_AMNEZIAWG


def test_defaults_for_routeros():
    model = ServerModel(name='test', type=ServerType.ROUTEROS)
    assert model.interface_name == DEFAULT_INTERFACE_NAME_ROUTEROS


def test_default_port_linux():
    model = ServerModel(name='test', type=ServerType.LINUX, server='1.2.3.4')  # type: ignore
    assert model.port == DEFAULT_PORT_SSH


def test_default_port_routeros():
    model = ServerModel(name='test', type=ServerType.ROUTEROS, server='wg.example.com')  # type: ignore
    assert model.port == DEFAULT_PORT_ROUTEROS_API


def test_dns_parsing_single():
    model = ServerModel(name='test', dns='1.1.1.1')  # type: ignore
    assert model.dns == IPv4Address('1.1.1.1')


def test_dns_parsing_multiple():
    model = ServerModel(name='test', dns='1.1.1.1, 8.8.8.8 ')  # type: ignore
    assert model.dns == [IPv4Address('1.1.1.1'), IPv4Address('8.8.8.8')]


@pytest.mark.parametrize('input_value', [None, ' ,'])
def test_defaults_dns_none(input_value):
    model = ServerModel(name='test', dns=input_value)
    assert model.dns is None


def test_dns_serialization_single():
    model = ServerModel(name='test', dns='8.8.8.8')  # type: ignore
    data = model.model_dump(mode='json')
    assert data['dns'] == '8.8.8.8'


def test_dns_serialization_multiple():
    model = ServerModel(name='test', dns='1.1.1.1, 1.0.0.1')  # type: ignore
    data = model.model_dump(mode='json')
    assert data['dns'] == '1.1.1.1,1.0.0.1'


def test_dns_serialization_none():
    model = ServerModel(name='test')
    data = model.model_dump(mode='json')
    assert data['dns'] is None


@pytest.mark.parametrize('input_value', ['1.1.1', 'abc', '999.999.999.999', '1.1.1.1, not-an-ip'])
def test_dns_invalid(input_value):
    with pytest.raises(ValidationError):
        ServerModel(name='test', dns=input_value)  # type: ignore


def test_alias_paths_flat():
    model = ServerModel(
        name='flat_aliases',
        interface_name='wg0',
        path_to_config='/etc/wireguard/wg0.conf',
        endpoint='wg.example.com',  # type: ignore
        server='1.2.3.4',  # type: ignore
        port=51820,
        username='root',
        password='toor',
    )

    assert model.name == 'flat_aliases'
    assert model.interface_name == 'wg0'
    assert model.path_to_config == '/etc/wireguard/wg0.conf'
    assert str(model.endpoint) == 'wg.example.com'
    assert str(model.server) == '1.2.3.4'
    assert model.port == 51820
    assert model.username == 'root'
    assert model.password == 'toor'


def test_alias_paths_nested():
    raw_data = {
        'name': 'nested_aliases',
        'data': {
            'interface': 'awg0',
            'config': '/etc/amnezia/amneziawg/awg0.conf',
            'endpoint': 'awg.example.com',
            'server': '5.6.7.8',
            'port': 9999,
            'username': 'admin',
            'password': 'secret',
        }
    }

    model = ServerModel.model_validate(raw_data)

    assert model.name == 'nested_aliases'
    assert model.interface_name == 'awg0'
    assert model.path_to_config == '/etc/amnezia/amneziawg/awg0.conf'
    assert str(model.endpoint) == 'awg.example.com'
    assert str(model.server) == '5.6.7.8'
    assert model.port == 9999
    assert model.username == 'admin'
    assert model.password == 'secret'


def test_validation_error_on_port_out_of_range():
    with pytest.raises(ValidationError):
        ServerModel(name='bad', port=70000)
