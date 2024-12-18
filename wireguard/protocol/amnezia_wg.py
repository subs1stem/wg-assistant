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

        params = ['jc', 'jmin', 'jmax', 's1', 's2', 'h1', 'h2', 'h3', 'h4']
        amnezia_wg_config = '\n'.join(f'{param} = {server_config.get(param, 0)}' for param in params)

        return base_wireguard_config + '\n' + amnezia_wg_config
