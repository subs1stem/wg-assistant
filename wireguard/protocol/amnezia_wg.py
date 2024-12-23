from wireguard.protocol.base import BaseProtocol
from wireguard.protocol.wireguard import WireguardProtocol


class AmneziaWGProtocol(BaseProtocol):
    """Class that provides the AmneziaWG protocol."""

    def build_client_config(
            self,
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
