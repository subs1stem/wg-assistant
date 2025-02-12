from abc import ABC, abstractmethod
from ipaddress import IPv4Interface, IPv4Address
from typing import Optional

from wireguard.protocol.base import BaseProtocol


class WireGuard(ABC):
    """Abstract base class for all WireGuard implementations."""

    def __init__(
            self,
            protocol: BaseProtocol,
            endpoint: str,
            interface_name: str,
    ) -> None:
        """Initialize a new instance of WireGuard.

        Args:
            protocol (BaseProtocol): The WireGuard protocol.
            endpoint (str): The WireGuard server endpoint.
            interface_name (str): The WireGuard interface name.

        Returns:
            None
        """
        self.protocol = protocol
        self.endpoint = endpoint
        self.interface_name = interface_name

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
