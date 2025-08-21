import pytest

from wg_assistant.wireguard.wireguard import WireGuard


@pytest.mark.parametrize(
    'config,expected',
    [
        (
                {
                    'Interface': {'Address': '192.168.1.1/24'},
                },
                '192.168.1.2/32',
        ),
        (
                {
                    'Interface': {'Address': '192.168.1.1/24'},
                    'Rick': {'AllowedIPs': '192.168.1.2/32'},
                    'Daryl': {'AllowedIPs': '192.168.1.3/32'},
                },
                '192.168.1.4/32',
        ),
        (
                {
                    'Interface': {'Address': '10.0.0.1/24'},
                    'Rick': {'AllowedIPs': '10.0.0.2/32'},
                    'Daryl': {'AllowedIPs': '10.0.0.5/32'},
                },
                '10.0.0.3/32',
        ),
        (

                {
                    'Interface': {'Address': '192.168.1.1/30'},
                    'Rick': {'AllowedIPs': '192.168.1.2/32'},
                    'Daryl': {'AllowedIPs': '192.168.1.3/32'},
                },
                None,
        ),
    ],
    ids=['no peers', 'sequential', 'non sequential', 'full network'],
)
def test_get_available_ip(config, expected):
    result = WireGuard.get_available_ip(config)
    assert result == expected
