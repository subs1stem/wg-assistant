import pytest

from wg_assistant.modules.message_builders import peers_message


@pytest.mark.parametrize('peers, expected_message', [
    ({}, 'Interface is inactive'),
    (
            {
                'peer1': {
                    'endpoint': '192.168.1.15:6657',
                    'allowed ips': '172.16.0.5/32',
                    'latest handshake': '1 minute, 6 seconds ago',
                    'transfer': '181.22 MiB received, 2.59 GiB sent'
                }
            },

            '<ins><b>peer1</b></ins>\n'
            '<b>Endpoint:</b> 192.168.1.15:6657\n'
            '<b>IP:</b> 172.16.0.5/32\n'
            '<b>Handshake:</b> 1 minute, 6 seconds ago\n'
            '<b>Transfer:</b> 181.22 MiB / 2.59 GiB \n\n'
    ),
    ({'peer2': {}}, '<ins><b>peer2</b></ins>\nunconnected\n\n'),
], ids=['inactive interface', 'connected peer', 'unconnected peer'])
def test_peers_message(peers, expected_message):
    result = peers_message(peers)
    assert result == expected_message
