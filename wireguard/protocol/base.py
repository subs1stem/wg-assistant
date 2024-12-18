from abc import ABC, abstractmethod


class BaseProtocol(ABC):
    """Abstract base class for all WireGuard protocols."""

    @abstractmethod
    def build_client_config(
            self,
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
