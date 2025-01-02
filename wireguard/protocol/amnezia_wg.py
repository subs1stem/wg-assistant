from wgconfig import WGConfig

from wireguard.protocol.base import BaseProtocol
from wireguard.protocol.wireguard import WireguardProtocol


class AmneziaWGProtocol(BaseProtocol):
    """Class that provides the AmneziaWG protocol."""

    @staticmethod
    def build_client_config(
            privkey: str,
            address: str,
            server_pubkey: str,
            endpoint: str,
            server_port: int,
            server_config: dict,
    ) -> str:
        base_wireguard_config = WireguardProtocol().build_client_config(
            privkey=privkey,
            address=address,
            server_pubkey=server_pubkey,
            endpoint=endpoint,
            server_port=server_port,
            server_config=server_config,
        )

        params = ['Jc', 'Jmin', 'Jmax', 'S1', 'S2', 'H1', 'H2', 'H3', 'H4']
        amnezia_wg_config = '\n'.join(f'{param} = {server_config.get('Interface').get(param, 0)}' for param in params)

        return base_wireguard_config + '\n' + amnezia_wg_config

    @staticmethod
    def parse_config_to_dict(config: str) -> dict:
        config_dict = {}
        current_section = 'Interface'
        section_content = {}
        pending_public_key = None

        for line in config.splitlines():
            line = line.removeprefix('#!').strip()

            if not line or line == '[Interface]':
                continue

            if line == '[Peer]':
                if current_section is None and pending_public_key:
                    current_section = pending_public_key

                if current_section:
                    config_dict[current_section] = section_content

                current_section = None
                pending_public_key = None
                section_content = {}

            else:
                key, value = (item.strip() for item in line.split(' = ', maxsplit=1))

                if key == '#_Name':
                    current_section = value
                elif key == 'PublicKey':
                    pending_public_key = value

                section_content[key] = value

        if current_section is None and pending_public_key:
            current_section = pending_public_key

        if current_section:
            config_dict[current_section] = section_content

        return config_dict

    @staticmethod
    def get_genkey_command() -> str:
        return 'awg genkey'

    @staticmethod
    def get_pubkey_command() -> str:
        return 'awg pubkey'

    @staticmethod
    def get_quick_command() -> str:
        return 'awg-quick'

    @staticmethod
    def get_show_command() -> str:
        return 'awg show'

    @staticmethod
    def add_peer(wg_config: WGConfig, pubkey: str, name: str) -> WGConfig:
        wg_config.add_peer(pubkey)
        wg_config.add_attr(pubkey, '#_Name', name)
        return wg_config
