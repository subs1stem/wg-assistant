from functools import wraps
from typing import Callable, Any, Tuple

from wgconfig import WGConfig

from wireguard.client.base import BaseClient
from wireguard.protocol.base import BaseProtocol
from wireguard.wireguard import WireGuard


class Linux(WireGuard):
    """Class for a WireGuard server deployed on a Linux host."""

    _TMP_CONFIG_PATH = '/tmp/wg0.conf'

    def __init__(
            self,
            client: BaseClient,
            protocol: BaseProtocol,
            endpoint: str,
            interface_name: str = 'wg0',
            path_to_config: str = '/etc/wireguard/wg0.conf'
    ) -> None:
        """Initialize a new instance of Linux WireGuard.

        Args:
            client (BaseClient): Client used to interact with the WireGuard host.
            protocol (BaseProtocol): The WireGuard protocol.
            endpoint (str): The WireGuard server endpoint.
            interface_name (str, optional): The WireGuard interface name. Default is ``wg0``.
            path_to_config (str, optional): The path to the WireGuard configuration file.
                Default is ``/etc/wireguard/wg0.conf``.

        Returns:
            None
        """
        super().__init__(protocol, endpoint, interface_name)

        self.client = client
        self.path_to_config = path_to_config

        self.wg_config = WGConfig(self._TMP_CONFIG_PATH)

    def _generate_key_pair(self) -> Tuple[str, str]:
        """Generate a WireGuard private-public key pair.

        Returns:
            Tuple[str, str]: A tuple containing private key and public key strings.
        """
        _, stdout, _ = self.client.execute(f'{self.protocol.get_command()} genkey')
        privkey = stdout.readline().strip()

        _, stdout, _ = self.client.execute(f'echo "{privkey}" | {self.protocol.get_command()} pubkey')
        pubkey = stdout.readline().strip()

        return privkey, pubkey

    @staticmethod
    def _config_operation(rewrite_config: bool = False) -> Callable[..., Any]:
        """Decorator for performing configuration-related operations.

        This decorator is used to wrap methods that involve configuration operations.
        It can download the configuration file, read it, execute the wrapped method,
        and optionally rewrite the configuration file and trigger a restart.

        Args:
            rewrite_config (bool, optional): Whether to rewrite the configuration file
                and trigger a restart the WireGuard server after executing the wrapped method.
                Default is False.

        Returns:
            Callable[..., Any]: A decorated method that handles configuration operations.
        """

        def decorator(method: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(method)
            def wrapper(self, *args, **kwargs) -> Any:
                with open(self._TMP_CONFIG_PATH, 'w') as f:
                    f.write(self.client.get_file_contents(self.path_to_config))

                self.wg_config.read_file()
                result = method(self, *args, **kwargs)

                if rewrite_config:
                    self.wg_config.write_file()

                    with open(self._TMP_CONFIG_PATH, 'r') as f:
                        self.client.put_file_contents(self.path_to_config, f.read())

                    self.sync_config()

                return result

            return wrapper

        return decorator

    def sync_config(self) -> None:
        """Synchronizes the WireGuard configuration without disrupting current peer sessions.

        Returns:
            None
        """
        self.client.execute(
            f"{self.protocol.get_command()} syncconf {self.interface_name} "
            f"<({self.protocol.get_quick_command()} strip {self.path_to_config})"
        )

    def reboot_host(self) -> None:
        self.client.execute('reboot')

    def get_config(self, as_dict: bool = False) -> str | dict:
        _, stdout, _ = self.client.execute(f'cat {self.path_to_config}')
        config = ''.join(stdout.readlines())
        return self.protocol.parse_config_to_dict(config) if as_dict else config

    def set_wg_enabled(self, enabled: bool) -> None:
        state = 'up' if enabled else 'down'
        self.client.execute(f'{self.protocol.get_quick_command()} {state} {self.interface_name}')

    def get_wg_enabled(self) -> bool:
        _, stdout, _ = self.client.execute(f'{self.protocol.get_command()} show {self.interface_name}')
        return bool(stdout.readline())

    def get_server_pubkey(self) -> str | None:
        _, stdout, stderr = self.client.execute(f'{self.protocol.get_command()} show {self.interface_name} public-key')
        return None if stderr.readline() else stdout.readline().strip()

    def get_peers(self) -> dict:
        _, stdout, stderr = self.client.execute(f'{self.protocol.get_command()} show {self.interface_name}')

        if stderr.read():
            return {}

        stdout_str = stdout.read()

        if isinstance(stdout_str, bytes):
            stdout_str = stdout_str.decode('utf-8')

        str_blocks = stdout_str.split('\n\n')

        config = self.get_config(as_dict=True)
        peer_names = {v.get('PublicKey', k): k for k, v in config.items()}

        peers = {}

        for block in str_blocks:
            unit = block.split('\n  ')
            key = unit.pop(0).split(':')[1].strip()

            if key != self.interface_name:
                inside_dict = {k.strip(): v.strip() for k, v in (item.split(':', 1) for item in unit)}
                peers[peer_names.get(key, key)] = inside_dict

        return peers

    @_config_operation(rewrite_config=True)
    def add_peer(self, name: str) -> str:
        server_config = self.get_config(as_dict=True)

        privkey, pubkey = self._generate_key_pair()
        peer_ip = self.get_available_ip(server_config)
        server_pubkey = self.get_server_pubkey()
        server_port = server_config.get('Interface').get('ListenPort')

        self.wg_config = self.protocol.add_peer(self.wg_config, pubkey, name)
        self.wg_config.add_attr(pubkey, 'AllowedIPs', peer_ip)

        client_config = self.protocol.build_client_config(
            privkey=privkey,
            address=peer_ip,
            server_pubkey=server_pubkey,
            endpoint=self.endpoint,
            server_port=server_port,
            server_config=server_config,
        )

        return client_config

    @_config_operation(rewrite_config=True)
    def delete_peer(self, pubkey: str) -> None:
        self.wg_config.del_peer(pubkey)

    @_config_operation(rewrite_config=True)
    def set_peer_enabled(self, pubkey: str, enabled: bool) -> None:
        if enabled:
            self.wg_config.enable_peer(pubkey)
        else:
            self.wg_config.disable_peer(pubkey)

    @_config_operation()
    def get_peer_enabled(self, pubkey: str) -> bool:
        return self.wg_config.get_peer_enabled(pubkey)

    @_config_operation(rewrite_config=True)
    def rename_peer(self, pubkey: str, new_name: str) -> None:
        self.wg_config = self.protocol.rename_peer(self.wg_config, pubkey, new_name)
