from wireguard.protocol.base import BaseProtocol


class WireguardProtocol(BaseProtocol):
    """Class that provides the standard WireGuard protocol."""

    def build_client_config(
            self,
            privkey: str,
            address: str,
            server_pubkey: str,
            endpoint: str,
            server_port: int,
            server_config: dict,
    ) -> str:
        wg_config = (
            '[Peer]\n'
            f'PublicKey = {server_pubkey}\n'
            'AllowedIPs = 0.0.0.0/0\n'
            f'Endpoint = {endpoint}:{server_port}\n'
            'PersistentKeepalive = 30\n\n'
            '[Interface]\n'
            f'PrivateKey = {privkey}\n'
            f'Address = {address}\n'
            'DNS = 1.1.1.1, 1.0.0.1'
        )

        return wg_config

    def get_genkey_command(self) -> str:
        return 'wg genkey'

    def get_pubkey_command(self) -> str:
        return 'wg pubkey'

    def get_quick_command(self) -> str:
        return 'wg-quick'

    def get_show_command(self) -> str:
        return 'wg show'
