def peers_message(peers):
    if not peers:
        return 'Interface is inactive'
    message = ''
    for key in peers:
        params = peers[key]
        message += f'<ins><b>{key}</b></ins>\n'
        try:
            endpoint = f'<b>Endpoint:</b> {params["endpoint"]}'
            ip = f'<b>IP:</b> {params["allowed ips"]}'
            handshake = f'<b>Handshake:</b> {params["latest handshake"]}'
            transfer = f'<b>Transfer:</b> ' \
                       f'{params["transfer"].replace("received", "").replace("sent", "").replace(",", "/")}'
            message += f'{endpoint}\n' \
                       f'{ip}\n' \
                       f'{handshake}\n' \
                       f'{transfer}\n\n'
        except KeyError:
            message += 'unconnected\n\n'
    return message
