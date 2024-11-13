from abc import ABC, abstractmethod
from ipaddress import IPv4Interface, IPv4Address
from typing import Optional


class WireGuard(ABC):
    """Abstract base class for a WireGuard server."""

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str,
            interface_name: str,
            endpoint: str | None = None,
    ) -> None:
        """Initialize a new instance of WireGuard client.

        Args:
            server (str): The server address.
            port (int): The port number for the connection.
            username (str): The username for authentication.
            password (str): The password for authentication.
            interface_name (str): The WireGuard interface name.
            endpoint (str | None): The WireGuard server endpoint. If ``None``, the ``server`` parameter is used.

        Returns:
            None
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.interface_name = interface_name
        self.endpoint = endpoint if endpoint is not None else server

    @staticmethod
    def build_client_config(
            privkey: str,
            address: str,
            server_pubkey: str,
            endpoint: str,
            server_port: int,
    ) -> str:
        """Generate a WireGuard client configuration.

        Args:
            privkey (str): The private key of the client.
            address (str): The client's assigned IP address.
            server_pubkey (str): The public key of the server.
            endpoint (str): The endpoint of the WireGuard server.
            server_port (int): The port number of the WireGuard server.

        Returns:
            str: A WireGuard configuration string with the provided parameters.
        """
        wg_config = '[Interface]\n' \
                    f'PrivateKey = {privkey}\n' \
                    f'Address = {address}\n' \
                    f'DNS = 1.1.1.1, 1.0.0.1\n\n' \
                    '[Peer]\n' \
                    f'PublicKey = {server_pubkey}\n' \
                    'AllowedIPs = 0.0.0.0/0\n' \
                    f'Endpoint = {endpoint}:{server_port}\n' \
                    'PersistentKeepalive = 30'

        return wg_config

    @staticmethod
    def get_available_ip(config: dict) -> Optional[str]:
        """Get an available IP address based on the provided configuration.

        Args:
            config (dict): A dictionary containing network configuration data.

        Returns:
            Optional[str]: The next available IP address in the format 'X.X.X.X/32',
            or None if there are no available IP addresses.
        """
        # Extract the interface IP address and subnet mask
        interface_ip_with_mask = config['Interface']['Address']
        interface_ip = IPv4Interface(interface_ip_with_mask)

        # Calculate the network from the interface's IP and mask
        network = interface_ip.network

        # Extract all used IP addresses and convert them to IPv4Address objects
        used_ips = [IPv4Address(config[key]['AllowedIPs'].split('/')[0]) for key in config if
                    key != 'Interface']

        # Iterate through the possible IP range in the network and find the first available IP,
        # skipping the interface IP.
        for ip in network.hosts():
            if ip != interface_ip.ip and ip not in used_ips:
                return f'{ip}/32'

        # If no available IP is found, return None
        return None

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
    def get_server_pubkey(self) -> str | None:
        """Get the public key of the WireGuard server.

        Return:
            str | None: The WireGuard server's public key, or "None" if an error occurred.
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
    def set_peer_enabled(self, pubkey: str, enabled: bool) -> None:
        """Enables or disables a WireGuard peer based on its public key.

        Args:
            pubkey (str): The public key of the peer to enable or disable.
            enabled (bool): If True, enables the peer. If False, disables the peer.

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

    @abstractmethod
    def rename_peer(self, pubkey: str, new_name: str) -> None:
        """Rename a peer in the WireGuard server.

        Args:
            pubkey (str): The public key of the peer to be renamed.
            new_name (str): The new name of the peer.

        Returns:
            None
        """
