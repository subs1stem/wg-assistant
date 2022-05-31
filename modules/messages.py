from wireguard.ssh import SSH
from settings import WG_INTERFACE_NAME


def peers_message():
    ssh = SSH()
    peers = ssh.get_peers()
    message = ''
    for key in peers:
        if key == WG_INTERFACE_NAME:
            continue
        params = peers[key]
        endpoint = f'<b>Endpoint:</b> {params["endpoint"]}'
        ip = f'<b>IP:</b> {params["allowed ips"]}'
        handshake = f'<b>Handshake:</b> {params["latest handshake"]}'
        transfer = f'<b>Transfer:</b> ' \
                   f'{params["transfer"].replace("received", "").replace("sent", "").replace(",", "/")}'
        message += f'<ins><b>{key}</b></ins>\n' \
                   f'{endpoint}\n' \
                   f'{ip}\n' \
                   f'{handshake}\n' \
                   f'{transfer}\n\n'
    return message
