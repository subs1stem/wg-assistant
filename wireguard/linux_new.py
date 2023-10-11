from functools import wraps
from time import sleep
from typing import Callable, Any

from paramiko import SSHClient, AutoAddPolicy
from wgconfig import WGConfig

from wireguard.wireguard import WireGuard


class Linux(WireGuard):
    """A class for a WireGuard server deployed on a Linux host."""

    tmp_config = '/tmp/wg0.conf'

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str,
            config: str = '/etc/wireguard/wg0.conf',
            interface: str = 'wg0',
    ) -> None:
        """Initialize a new instance of Linux WireGuard client.

        Args:
            server (str): The server address.
            port (int): The port number for the connection.
            username (str): The username for authentication.
            password (str): The password for authentication.
            config (str, optional): The path to the WireGuard configuration file.
                Defaults to '/etc/wireguard/wg0.conf'.
            interface (str, optional): The WireGuard interface name. Defaults to 'wg0'.

        Returns:
            None
        """
        super().__init__(server, port, username, password)

        self.config = config
        self.interface = interface
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.connect()

        self.wg_config = WGConfig(self.tmp_config)

    def __del__(self) -> None:
        self.client.close()

    def _download_config(self) -> None:
        """Download the WireGuard server configuration file to the local temporary file.

        Returns:
            None
        """
        self.client.open_sftp().get(self.config, self.tmp_config)

    def _upload_config(self) -> None:
        """Upload the local temporary WireGuard configuration file to the remote host.

        Returns:
            None
        """
        self.client.open_sftp().put(self.tmp_config, self.config)

    @staticmethod
    def _config_operation(rewrite_config: bool = False) -> Callable[..., Any]:
        """Decorator for performing configuration-related operations.

        This decorator is used to wrap methods that involve configuration operations.
        It can download the configuration file, read it, execute the wrapped method,
        and optionally rewrite the configuration file and trigger a restart.

        Args:
            rewrite_config (bool, optional): Whether to rewrite the configuration file
                and trigger a restart the WireGuard server after executing the wrapped method.
                Defaults to False.

        Returns:
            Callable[..., Any]: A decorated method that handles configuration operations.
        """

        def decorator(method: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(method)
            def wrapper(self, *args, **kwargs) -> Any:
                self._download_config()
                self.wg_config.read_file()
                result = method(self, *args, **kwargs)

                if rewrite_config:
                    self.wg_config.write_file()
                    self._upload_config()
                    self.restart()

                return result

            return wrapper

        return decorator

    def connect(self) -> None:
        try:
            self.client.connect(hostname=self.server,
                                username=self.username,
                                password=self.password,
                                port=self.port)
        except Exception:
            raise ConnectionError('Error connecting to WireGuard server host')

    def reboot_host(self) -> None:
        self.client.exec_command('reboot')

    def get_config(self) -> str:
        _, stdout, _ = self.client.exec_command(f'cat {self.config}')
        return ''.join(stdout.readlines())

    def set_wg_enabled(self, enabled: bool) -> None:
        state = 'up' if enabled else 'down'
        self.client.exec_command(f'wg-quick {state} {self.interface}')

    def restart(self) -> None:
        self.set_wg_enabled(False)
        sleep(3)
        self.set_wg_enabled(True)

    def get_peers(self) -> dict:
        # if not self.get_wg_status():
        #     return False
        _, stdout, _ = self.client.exec_command(f'wg show {self.interface}')
        # peer_names = self.get_peer_names()
        str_blocks = stdout.read().decode().split('\n\n')
        peers = {}
        for block in str_blocks:
            unit = block.split('\n  ')
            key = unit.pop(0).split(':')[1].strip()
            if key == self.interface:
                continue
            # try:
            #     peer_name = peer_names[key]
            # except KeyError:
            #     peer_name = key
            # peers[peer_name] = None
            inside_dict = {}
            for item in unit:
                inside_key, inside_value = item.split(':', 1)
                inside_dict[inside_key.strip()] = inside_value.strip()
            peers[key] = inside_dict
        return peers

    def add_peer(self, name: str) -> None:
        pass

    @_config_operation(rewrite_config=True)
    def del_peer(self, pubkey: str) -> None:
        self.wg_config.del_peer(pubkey)

    @_config_operation(rewrite_config=True)
    def enable_peer(self, pubkey: str) -> None:
        self.wg_config.enable_peer(pubkey)

    @_config_operation(rewrite_config=True)
    def disable_peer(self, pubkey: str) -> None:
        self.wg_config.disable_peer(pubkey)

    @_config_operation()
    def get_peer_enabled(self, pubkey: str) -> bool:
        return self.wg_config.get_peer_enabled(pubkey)
