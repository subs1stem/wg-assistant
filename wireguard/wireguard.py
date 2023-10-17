from abc import ABC, abstractmethod


class WireGuard(ABC):
    """Abstract base class for a WireGuard server."""

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str
    ) -> None:
        """Initialize a new instance of WireGuard client.

        Args:
            server (str): The server address.
            port (int): The port number for the connection.
            username (str): The username for authentication.
            password (str): The password for authentication.

        Returns:
            None
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    @staticmethod
    def get_client_config(privkey, address, pubkey, server_ip, server_port):
        """Generate a WireGuard client configuration.

        Args:
            privkey (str): The private key of the client.
            address (str): The client's assigned IP address.
            pubkey (str): The public key of the server.
            server_ip (str): The IP address of the WireGuard server.
            server_port (int): The port number of the WireGuard server.

        Returns:
            str: A WireGuard configuration string with the provided parameters.
        """
        wg_config = '[Interface]\n' \
                    f'PrivateKey = {privkey}\n' \
                    f'Address = {address}\n' \
                    f'DNS = 8.8.8.8\n\n' \
                    '[Peer]\n' \
                    f'PublicKey = {pubkey}\n' \
                    'AllowedIPs = 0.0.0.0/0\n' \
                    f'Endpoint = {server_ip}:{server_port}\n' \
                    'PersistentKeepalive = 30'
        return wg_config

    @abstractmethod
    def connect(self) -> None:
        """Connect to the WireGuard server.

        Returns:
            None

        Raises:
            ConnectionError: If the connection to the WireGuard server host fails.
        """

    @abstractmethod
    def reboot_host(self) -> None:
        """Reboot the host system.

        Returns:
            None
        """

    @abstractmethod
    def get_config(self, as_dict: bool = False) -> str | dict:
        """Get the WireGuard server configuration.

        Args:
            as_dict (bool, optional): If True, return the configuration as a dictionary.
                If False (default), return it as a string.

        Returns:
            str | dict: The WireGuard server configuration.
        """

    @abstractmethod
    def set_wg_enabled(self, enabled: bool) -> None:
        """Enable or disable the WireGuard interface.

        Args:
            enabled (bool): True to enable, False to disable.

        Returns:
            None
        """

    @abstractmethod
    def get_wg_enabled(self) -> bool:
        """Get the status of the WireGuard interface.

        Returns:
            bool: True if the WireGuard interface is enabled, False if it's disabled.
        """

    @abstractmethod
    def restart(self) -> None:
        """Restart the WireGuard server.

        Returns:
            None
        """

    @abstractmethod
    def get_peers(self) -> dict:
        """Get a list of all configured peers.

        Returns:
            list: A list of peer.
        """

    @abstractmethod
    def add_peer(self, name: str) -> str:
        """Add a new peer to the WireGuard server.

        Args:
            name (str): The name of the peer.

        Returns:
            str: The WireGuard client configuration for the new peer.
        """

    @abstractmethod
    def delete_peer(self, pubkey: str) -> None:
        """Delete a peer from the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be deleted.

        Returns:
            None
        """

    @abstractmethod
    def enable_peer(self, pubkey: str) -> None:
        """Enable a peer in the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be enabled.

        Returns:
            None
        """

    @abstractmethod
    def disable_peer(self, pubkey: str) -> None:
        """Disable a peer in the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be disabled.

        Returns:
            None
        """

    @abstractmethod
    def get_peer_enabled(self, pubkey: str) -> bool:
        """Check if a peer is enabled in the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be checked.

        Returns:
            bool: True if the peer is enabled, False otherwise.
        """
