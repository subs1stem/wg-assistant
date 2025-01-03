from abc import ABC, abstractmethod

from wgconfig import WGConfig


class BaseProtocol(ABC):
    """Abstract base class for all WireGuard protocols."""

    @staticmethod
    @abstractmethod
    def build_client_config(
            privkey: str,
            address: str,
            server_pubkey: str,
            endpoint: str,
            server_port: int,
            server_config: dict,
    ) -> str:
        """Generate a WireGuard client configuration.

        Args:
            privkey (str): The private key of the client.
            address (str): The client's assigned IP address.
            server_pubkey (str): The public key of the server.
            endpoint (str): The address of the WireGuard server.
            server_port (int): The port number of the WireGuard server.
            server_config (dict): The configuration of the WireGuard server.

        Returns:
            str: A WireGuard configuration string with the provided parameters.
        """

    @staticmethod
    @abstractmethod
    def parse_config_to_dict(config: str) -> dict:
        """Parse a WireGuard server configuration string and convert it into a dictionary.

        Args:
            config (str): The WireGuard server configuration as a string.

        Returns:
            dict: A dictionary representation of the WireGuard server configuration.
        """

    @staticmethod
    @abstractmethod
    def get_genkey_command() -> str:
        """Retrieves the ``genkey`` command.

        Returns:
            str: The command string for generating a key pair.
        """

    @staticmethod
    @abstractmethod
    def get_pubkey_command() -> str:
        """Retrieves the ``pubkey`` command.

        Returns:
            str: The command string for obtaining the public key.
        """

    @staticmethod
    @abstractmethod
    def get_quick_command() -> str:
        """Retrieves the ``wg-quick`` command.

        Returns:
            str: The command string for running the ``wg-quick`` tool.
        """

    @staticmethod
    @abstractmethod
    def get_show_command() -> str:
        """Retrieves the ``show`` command.

        Returns:
            str: The command string for running the ``show`` command.
        """

    @staticmethod
    @abstractmethod
    def add_peer(wg_config: WGConfig, pubkey: str, name: str) -> WGConfig:
        """Add a peer to the given WireGuard configuration.

        This method is responsible for adding a peer's public key and associated metadata
        (such as name) to the WireGuard configuration. The exact implementation of how
        the peer is added must be defined in a subclass.

        Args:
            wg_config (WGConfig): The ``WGConfig`` class instance to which the peer will be added.
            pubkey (str): The public key of the peer.
            name (str): A descriptive name or identifier for the peer.

        Returns:
            WGConfig: The updated ``WGConfig`` configuration instance with the new peer added.
        """

    @staticmethod
    @abstractmethod
    def rename_peer(wg_config: WGConfig, pubkey: str, new_name: str) -> WGConfig:
        """Rename a peer in the given WireGuard configuration.

        This method is responsible for updating the name or identifier associated
        with a specific peer in the WireGuard configuration. The exact implementation
        must be defined in a subclass.

        Args:
            wg_config (WGConfig): The ``WGConfig`` class instance containing the peer to rename.
            pubkey (str): The public key of the peer whose name is to be updated.
            new_name (str): The new name or identifier to assign to the peer.

        Returns:
            WGConfig: The updated ``WGConfig`` configuration instance with the peer renamed.
        """
