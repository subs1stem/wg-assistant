from routeros_api import RouterOsApiPool

from wireguard.wireguard import WireGuard


class RouterOS(WireGuard):
    """Class for WireGuard server deployed on RouterOS."""

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str
    ) -> None:
        """Initialize a new instance of the RouterOS WireGuard client.

        Args:
            server (str): The server address.
            port (int): The port number for the connection.
            username (str): The username for authentication.
            password (str): The password for authentication.

        Returns:
            None
        """
        super().__init__(server, port, username, password)

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

    def connect(self) -> None:
        pass

    def reboot_host(self) -> None:
        self.api.get_binary_resource('/').call('system/reboot')

    def get_config(self, as_dict: bool = False) -> str | dict:
        pass

    def set_wg_enabled(self, enabled: bool) -> None:
        pass

    def get_wg_enabled(self) -> bool:
        pass

    def get_server_pubkey(self) -> str | None:
        pass

    def restart(self) -> None:
        pass

    def get_peers(self) -> list:
        pass

    def add_peer(self, name: str) -> None:
        pass

    def delete_peer(self, pubkey: str) -> None:
        pass

    def enable_peer(self, pubkey: str) -> None:
        pass

    def disable_peer(self, pubkey: str) -> None:
        pass

    def get_peer_enabled(self, pubkey: str) -> bool:
        pass

    def rename_peer(self, pubkey: str, new_name: str) -> None:
        pass
