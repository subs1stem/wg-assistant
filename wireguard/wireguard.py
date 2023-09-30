from abc import ABC, abstractmethod


class WireGuard(ABC):
    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str
    ) -> None:
        """
        Initialize a WireGuard server instance.

        :param server: WireGuard server host address.
        :param port: Port for connecting to the WireGuard server host.
        :param username: Username for authentication on host.
        :param password: Password for authentication on host.
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    @abstractmethod
    def connect(self) -> None:
        """Connect to the WireGuard server host."""

    @abstractmethod
    def reboot_host(self) -> None:
        """Reboot the WireGuard server host."""

    @abstractmethod
    def get_config_raw(self) -> str:
        """
        Get the raw configuration of the WireGuard server.

        :return: The raw configuration as a string.
        """

    @abstractmethod
    def change_state(self, state: bool) -> None:
        """Change the state of the WireGuard interface."""

    @abstractmethod
    def restart(self) -> None:
        """Restart the WireGuard service."""

    @abstractmethod
    def get_peers(self) -> list:
        """
        Get a list of peers connected to the WireGuard server.

        :return: A list of peer information.
        """

    @abstractmethod
    def add_peer(self, name: str) -> None:
        """Add a new peer to the WireGuard server."""

    @abstractmethod
    def del_peer(self, pubkey: str) -> None:
        """Delete a peer from the WireGuard server."""

    @abstractmethod
    def enable_peer(self, pubkey: str) -> None:
        """Enable a peer on the WireGuard server."""

    @abstractmethod
    def disable_peer(self, pubkey: str) -> None:
        """Disable a peer on the WireGuard server."""

    @abstractmethod
    def get_peer_enabled(self, pubkey: str) -> bool:
        """
        Checks whether the peer is enabled.

        :return: True if the peer is enabled, False otherwise.
        """
