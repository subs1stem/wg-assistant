from wgconfig import WGConfig

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
    def get_command() -> str:
        return 'wg'

    @staticmethod
    def get_quick_command() -> str:
        return 'wg-quick'

    @staticmethod
    def add_peer(wg_config: WGConfig, pubkey: str, name: str) -> WGConfig:
        wg_config.add_peer(pubkey, '# ' + name)
        return wg_config

    @staticmethod
    def rename_peer(wg_config: WGConfig, pubkey: str, new_name: str) -> WGConfig:
        section_start_position = wg_config.get_sectioninfo(pubkey)[0]
        first_line = wg_config.lines[section_start_position]

        # Check if a line is a comment
        if first_line.startswith('#'):
            wg_config.lines[section_start_position] = '# ' + new_name

        return wg_config
