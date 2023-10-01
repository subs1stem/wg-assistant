from abc import ABC, abstractmethod


class WGInterface(ABC):
    """Abstract base class for a WireGuard server."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the WireGuard server.

        Raises:
            ConnectionError: If the connection to the WireGuard server host fails.
        """

    @abstractmethod
    def reboot_host(self) -> None:
        """Reboot the host system."""

    @abstractmethod
    def get_config_raw(self) -> str:
        """Get the raw configuration of the WireGuard server.

        Returns:
            str: The raw configuration as a string.
        """

    @abstractmethod
    def set_wg_enabled(self, enabled: bool) -> None:
        """Enable or disable the WireGuard interface.

        Args:
            enabled (bool): True to enable, False to disable.
        """

    @abstractmethod
    def restart(self) -> None:
        """Restart the WireGuard server."""

    @abstractmethod
    def get_peers(self) -> list:
        """Get a list of all configured peers.

        Returns:
            list: A list of peer.
        """

    @abstractmethod
    def add_peer(self, name: str) -> None:
        """Add a new peer to the WireGuard server.

        Args:
            name (str): The name of the new peer.
        """

    @abstractmethod
    def del_peer(self, pubkey: str) -> None:
        """Delete a peer from the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be deleted.
        """

    @abstractmethod
    def enable_peer(self, pubkey: str) -> None:
        """Enable a peer in the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be enabled.
        """

    @abstractmethod
    def disable_peer(self, pubkey: str) -> None:
        """Disable a peer in the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be disabled.
        """

    @abstractmethod
    def get_peer_enabled(self, pubkey: str) -> bool:
        """Check if a peer is enabled in the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be checked.

        Returns:
            bool: True if the peer is enabled, False otherwise.
        """
