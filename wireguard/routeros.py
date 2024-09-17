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
            interface_name: str,
    ) -> None:
        """Initialize a new instance of the RouterOS WireGuard client.

        Args:
            server (str): The server address.
            port (int): The port number for the connection.
            username (str): The username for authentication.
            password (str): The password for authentication.
            interface_name (str): The WireGuard interface name.

        Returns:
            None
        """
        super().__init__(server, port, username, password)
        self.interface_name = interface_name

        self.connection = RouterOsApiPool(
            host=self.server,
            username=self.username,
            password=self.password,
            port=self.port,
            plaintext_login=True,
        )

        self.api = self.connection.get_api()

    def __del__(self) -> None:
        self.connection.disconnect()

    def _get_interface(self) -> dict[str, Any] | None:
        """Retrieves the WireGuard interface details by its name.

        Returns:
            dict[str, Any] | None: A dictionary containing the interface details if found, otherwise None.
        """
        interface = self.api.get_resource('/interface/wireguard').get(name=self.interface_name)
        return interface[0] if interface else None

    def _set_peer_enabled(self, pubkey: str, enabled: bool) -> None:
        """Enables or disables a WireGuard peer based on its public key.

        Args:
            pubkey (str): The public key of the peer to enable or disable.
            enabled (bool): If True, enables the peer. If False, disables the peer.
        """
        # TODO: Consider making this method public and replacing `enable_peer` and `disable_peer`.
        peer = self.api.get_resource('/interface/wireguard/peers').get(public_key=pubkey)
        if peer:
            self.api.get_resource('/interface/wireguard/peers').set(
                id=peer[0]['id'],
                disabled='no' if enabled else 'yes'
            )

    def connect(self) -> None:
        pass

    def reboot_host(self) -> None:
        self.api.get_binary_resource('/').call('system/reboot')

    def get_config(self, as_dict: bool = False) -> str | dict:
        pass

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

    def get_peers(self) -> list:
        return self.api.get_resource('/interface/wireguard/peers').get(interface=self.interface_name)

    def add_peer(self, name: str) -> None:
        pass

    def delete_peer(self, pubkey: str) -> None:
        pass

    def enable_peer(self, pubkey: str) -> None:
        self._set_peer_enabled(pubkey, enabled=True)

    def disable_peer(self, pubkey: str) -> None:
        self._set_peer_enabled(pubkey, enabled=False)

    def get_peer_enabled(self, pubkey: str) -> bool:
        pass

    def rename_peer(self, pubkey: str, new_name: str) -> None:
        pass
