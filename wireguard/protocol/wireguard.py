from wireguard.protocol.base import BaseProtocol


class WireguardProtocol(BaseProtocol):
    """Class that provides the standard WireGuard protocol."""

    @staticmethod
    def build_client_config(
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

    @staticmethod
    def parse_config_to_dict(config: str) -> dict:
        config_dict = {}
        now_section_name = 'Interface'
        now_section_content = {}

        for line in config.splitlines():
            line = line.replace('#!', '').strip()

            if line.startswith('# '):
                config_dict[now_section_name] = now_section_content
                now_section_content = {}
                now_section_name = line.lstrip('# ').rstrip()

            elif line and not line.startswith('['):
                line = line.lstrip('#!')
                key, value = (item.strip() for item in line.split(' = '))
                now_section_content[key] = value

        config_dict[now_section_name] = now_section_content
        return config_dict

    @staticmethod
    def get_genkey_command() -> str:
        return 'wg genkey'

    @staticmethod
    def get_pubkey_command() -> str:
        return 'wg pubkey'

    @staticmethod
    def get_quick_command() -> str:
        return 'wg-quick'

    @staticmethod
    def get_show_command() -> str:
        return 'wg show'
