from ipaddress import IPv4Address, IPv6Address

from wgconfig import WGConfig

from src.wg_assistant.wireguard.protocol.base import BaseProtocol
from src.wg_assistant.wireguard.protocol.wireguard import WireguardProtocol


class AmneziaWGProtocol(BaseProtocol):
    """Class that provides the AmneziaWG protocol."""

    NAME_ATTR: str = '#_Name'

    def build_client_config(
            self,
            privkey: str,
            address: str,
            server_pubkey: str,
            server_port: int,
            server_external_ip: IPv4Address | IPv6Address | None = None,
            server_config: dict | None = None,
    ) -> str:
        base_wireguard_config = WireguardProtocol(self.endpoint, self.dns).build_client_config(
            privkey=privkey,
            address=address,
            server_pubkey=server_pubkey,
            server_port=server_port,
            server_external_ip=server_external_ip,
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

                if key == AmneziaWGProtocol.NAME_ATTR:
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
    def get_command() -> str:
        return 'awg'

    @staticmethod
    def get_quick_command() -> str:
        return 'awg-quick'

    @staticmethod
    def add_peer(wg_config: WGConfig, pubkey: str, name: str) -> WGConfig:
        wg_config.add_peer(pubkey)
        wg_config.add_attr(pubkey, AmneziaWGProtocol.NAME_ATTR, name)
        return wg_config

    @staticmethod
    def rename_peer(wg_config: WGConfig, pubkey: str, new_name: str) -> WGConfig:
        if wg_config.get_peer_enabled(pubkey):
            wg_config.del_attr(key=pubkey, attr=AmneziaWGProtocol.NAME_ATTR)
            wg_config.add_attr(key=pubkey, attr=AmneziaWGProtocol.NAME_ATTR, value=new_name)
        else:
            # Cannot change a disabled peer's attribute using del_attr() and add_attr()
            for i, line in enumerate(wg_config.lines):
                if line.startswith(f'#! {AmneziaWGProtocol.NAME_ATTR}'):
                    wg_config.lines[i] = f'#! {AmneziaWGProtocol.NAME_ATTR} = {new_name}'
                    break

        return wg_config
