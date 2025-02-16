from models.servers import Protocol, ServerType, Server
from wireguard.client.local import LocalClient
from wireguard.client.remote import RemoteClient
from wireguard.linux import Linux
from wireguard.protocol.amnezia_wg import AmneziaWGProtocol
from wireguard.protocol.base import BaseProtocol
from wireguard.protocol.wireguard import WireguardProtocol
from wireguard.routeros import RouterOS
from wireguard.wireguard import WireGuard


class ServerFactory:
    _instance = None
    _created_servers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def create_server_instance(cls, server_name: str, server: Server) -> WireGuard:
        """Create or retrieve a WireGuard server instance based on the provided server name and configuration.

        Args:
            server_name (str): The name of the server.
            server (Server): Server model.

        Returns:
            WireGuard: An instance of the WireGuard server.

        Raises:
            ValueError: If required data is missing or the server type is unrecognized.
        """
        if server_name in cls._created_servers:
            return cls._created_servers[server_name]

        protocol = cls._get_protocol(server)
        instance = cls._create_instance(server, protocol)

        cls._created_servers[server_name] = instance
        return instance

    @staticmethod
    def _get_protocol(server: Server) -> BaseProtocol:
        """Return the appropriate protocol instance based on the protocol type."""
        match server.protocol:
            case Protocol.WIREGUARD:
                return WireguardProtocol()
            case Protocol.AMNEZIA_WG:
                return AmneziaWGProtocol()
            case _:
                raise ValueError(f'Unhandled protocol type: {server.protocol.value}')

    @staticmethod
    def _create_instance(server_model: Server, protocol: BaseProtocol) -> WireGuard:
        """Instantiate and return the appropriate server type."""
        match server_model.type:
            case ServerType.LINUX:
                client = ServerFactory._get_linux_client(server_model)

                return Linux(
                    client=client,
                    protocol=protocol,
                    endpoint=str(server_model.endpoint),
                    interface_name=server_model.interface_name,
                    path_to_config=server_model.path_to_config,
                )

            case ServerType.ROUTEROS:
                return RouterOS(
                    server=str(server_model.server),
                    port=server_model.port,
                    username=server_model.username,
                    password=server_model.password,
                    protocol=protocol,
                    endpoint=str(server_model.endpoint),
                    interface_name=server_model.interface_name,
                )

            case _:
                raise ValueError(f'Unhandled server type: {server_model.type.value}')

    @staticmethod
    def _get_linux_client(server_model: Server) -> LocalClient | RemoteClient:
        """Determine and return the appropriate client for Linux servers."""
        if server_model.server is None:
            return LocalClient()

        return RemoteClient(
            server=str(server_model.server),
            port=server_model.port,
            username=server_model.username,
            password=server_model.password,
            key_filename=server_model.key_filename,
        )
