from typing import Any

from routeros_api import RouterOsApiPool

from wireguard.wireguard import WireGuard


class RouterOS(WireGuard):
    """Class for WireGuard server deployed on RouterOS."""

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str,
            interface_name: str = 'wireguard1',
    ) -> None:
        """Initialize a new instance of the RouterOS WireGuard client.

        Args:
            server (str): The server address.
            port (int): The port number for the connection.
            username (str): The username for authentication.
            password (str): The password for authentication.
            interface_name (str, optional): The WireGuard interface name. Defaults to 'wireguard1'.

        Returns:
            None
        """
        super().__init__(server, port, username, password, interface_name)

        self.connection = RouterOsApiPool(
            host=self.server,
            username=self.username,
            password=self.password,
            port=self.port,
            plaintext_login=True,
        )

        self.api = self.connection.get_api()

    @staticmethod
    def _format_config_as_string(config: dict) -> str:
        """Formats the WireGuard configuration dictionary as a string.

        Args:
            config (dict): The WireGuard configuration dictionary.

        Returns:
            str: The WireGuard configuration as a string, ending with a newline.
        """
        lines = ['[Interface]']
        lines.extend(f'{key} = {value}' for key, value in config['Interface'].items())

        for peer_name, peer_config in config.items():
            if peer_name != 'Interface':
                lines.append(f'\n# {peer_name}\n[Peer]')
                lines.extend(f'{key} = {value}' for key, value in peer_config.items())

        return '\n'.join(lines) + '\n'

    def _get_interface(self) -> dict[str, Any] | None:
        """Retrieves the WireGuard interface details by its name.

        Returns:
            dict[str, Any] | None: A dictionary containing the interface details if found, otherwise None.
        """
        interface = self.api.get_resource('/interface/wireguard').get(name=self.interface_name)
        return interface[0] if interface else None

    def _get_peer(self, pubkey: str) -> dict[str, Any] | None:
        """Retrieves the WireGuard peer details by its public key.

        Args:
            pubkey (str): The public key of the peer.

        Returns:
            dict[str, Any] | None: A dictionary containing the peer details if found, otherwise None.
        """
        peer = self.api.get_resource('/interface/wireguard/peers').get(public_key=pubkey)
        return peer[0] if peer else None

    def _set_peer_enabled(self, pubkey: str, enabled: bool) -> None:
        """Enables or disables a WireGuard peer based on its public key.

        Args:
            pubkey (str): The public key of the peer to enable or disable.
            enabled (bool): If True, enables the peer. If False, disables the peer.
        """
        # TODO: Consider making this method public and replacing `enable_peer` and `disable_peer`.
        peer = self._get_peer(pubkey)
        if peer:
            self.api.get_resource('/interface/wireguard/peers').set(
                id=peer['id'],
                disabled='no' if enabled else 'yes'
            )

    def connect(self) -> None:
        pass

    def reboot_host(self) -> None:
        self.api.get_binary_resource('/').call('system/reboot')

    def get_config(self, as_dict: bool = False) -> str | dict:
        interface = self._get_interface()
        address = self.api.get_resource('/ip/address').get(interface=self.interface_name)[0]

        config = {
            'Interface': {
                'PrivateKey': interface.get('private-key'),
                'ListenPort': interface.get('listen-port'),
                'Address': address.get('address'),
            }
        }

        peers = self.api.get_resource('/interface/wireguard/peers').get(interface=self.interface_name)

        for peer in peers:
            peer_name = peer.get('name')
            config[peer_name] = {
                'PublicKey': peer.get('public-key'),
                'AllowedIPs': peer.get('allowed-address'),
            }

        return config if as_dict else self._format_config_as_string(config)

    def set_wg_enabled(self, enabled: bool) -> None:
        interface = self._get_interface()
        if interface:
            self.api.get_resource('/interface/wireguard').set(
                id=interface['id'],
                disabled='no' if enabled else 'yes'
            )

    def get_wg_enabled(self) -> bool:
        interface = self._get_interface()
        return bool(interface and interface.get('disabled') == 'false')

    def get_server_pubkey(self) -> str | None:
        interface = self._get_interface()
        if interface:
            return interface.get('public-key')
        return None

    def restart(self) -> None:
        interface = self._get_interface()
        if interface:
            resource = self.api.get_resource('/interface/wireguard')
            resource.set(id=interface['id'], disabled='yes')
            resource.set(id=interface['id'], disabled='no')

    def get_peers(self) -> dict:
        raw_peers = self.api.get_resource('/interface/wireguard/peers').get(interface=self.interface_name)

        return {
            peer['name']: {
                'endpoint': f'{peer.get('current-endpoint-address')}:{peer.get('current-endpoint-port')}',
                'allowed ips': peer.get('allowed-address'),
                'latest handshake': peer.get('last-handshake'),
                'transfer': f'{peer.get('rx')} , {peer.get('tx')}',
            }
            for peer in raw_peers
        }

    def add_peer(self, name: str) -> str:
        interface = self._get_interface()
        config = self.get_config(as_dict=True)

        peers_resource = self.api.get_resource('/interface/wireguard/peers')

        peers_resource.add(
            name=name,
            interface=self.interface_name,
            private_key='auto',
            allowed_address=self.get_available_ip(config),
        )

        peer = peers_resource.get(name=name)[0]

        client_config = self.build_client_config(
            privkey=peer.get('private-key'),
            address=peer.get('allowed-address'),
            server_pubkey=self.get_server_pubkey(),
            server_ip=self.server,
            server_port=interface.get('listen-port'),
        )

        return client_config

    def delete_peer(self, pubkey: str) -> None:
        peer = self._get_peer(pubkey)
        if peer:
            self.api.get_resource('/interface/wireguard/peers').remove(id=peer['id'])

    def enable_peer(self, pubkey: str) -> None:
        self._set_peer_enabled(pubkey, enabled=True)

    def disable_peer(self, pubkey: str) -> None:
        self._set_peer_enabled(pubkey, enabled=False)

    def get_peer_enabled(self, pubkey: str) -> bool:
        peer = self._get_peer(pubkey)
        if peer:
            return peer.get('disabled') == 'false'
        return False

    def rename_peer(self, pubkey: str, new_name: str) -> None:
        peer = self._get_peer(pubkey)
        if peer:
            self.api.get_resource('/interface/wireguard/peers').set(
                id=peer['id'],
                name=new_name
            )
