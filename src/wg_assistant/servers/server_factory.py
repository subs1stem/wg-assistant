from src.wg_assistant.models.servers import Protocol, ServerType, ServerModel
from src.wg_assistant.wireguard.client.local import LocalClient
from src.wg_assistant.wireguard.client.remote import RemoteClient
from src.wg_assistant.wireguard.linux import Linux
from src.wg_assistant.wireguard.protocol.amnezia_wg import AmneziaWGProtocol
from src.wg_assistant.wireguard.protocol.base import BaseProtocol
from src.wg_assistant.wireguard.protocol.wireguard import WireguardProtocol
from src.wg_assistant.wireguard.routeros import RouterOS
from src.wg_assistant.wireguard.wireguard import WireGuard


class ServerFactory:
    _instance = None
    _created_servers: dict[str, WireGuard] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def create_server_instance(cls, server_model: ServerModel) -> WireGuard:
        """Create or retrieve a WireGuard server instance based on the provided server name and configuration.

        Args:
            server_model (ServerModel): Server model.

        Returns:
            WireGuard: An instance of the WireGuard server.
        """
        server_name = server_model.name

        if server_name in cls._created_servers:
            return cls._created_servers[server_name]

        protocol = cls._get_protocol(server_model)
        instance = cls._create_instance(server_model, protocol)

        cls._created_servers[server_name] = instance
        return instance

    @staticmethod
    def _get_protocol(server_model: ServerModel) -> BaseProtocol:
        """Return the appropriate protocol instance based on the protocol type."""
        match server_model.protocol:
            case Protocol.WIREGUARD:
                return WireguardProtocol(server_model.endpoint, server_model.dns)
            case Protocol.AMNEZIA_WG:
                return AmneziaWGProtocol(server_model.endpoint, server_model.dns)
            case _:
                raise ValueError(f'Unhandled protocol type: {server_model.protocol.value}')

    @staticmethod
    def _create_instance(server_model: ServerModel, protocol: BaseProtocol) -> WireGuard:
        """Instantiate and return the appropriate server type."""
        match server_model.type:
            case ServerType.LINUX:
                return Linux(
                    client=ServerFactory._get_linux_client(server_model),
                    protocol=protocol,
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
                    interface_name=server_model.interface_name,
                )

            case _:
                raise ValueError(f'Unhandled server type: {server_model.type.value}')

    @staticmethod
    def _get_linux_client(server_model: ServerModel) -> LocalClient | RemoteClient:
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
