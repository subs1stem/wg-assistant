from asyncio import sleep

from paramiko import SSHClient, AutoAddPolicy
from wgconfig import WGConfig

from wireguard.wireguard import WireGuard


class Linux(WireGuard):
    """A class for a WireGuard server deployed on a Linux host."""

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

    def __del__(self) -> None:
        self.client.close()

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

    def get_config_raw(self) -> str:
        _, stdout, _ = self.client.exec_command(f'cat {self.config}')
        return ''.join(stdout.readlines())

    def set_wg_enabled(self, enabled: bool) -> None:
        state = 'up' if enabled else 'down'
        self.client.exec_command(f'wg-quick {state} {self.interface}')

    def restart(self) -> None:
        self.set_wg_enabled(False)
        sleep(3)
        self.set_wg_enabled(True)

    def get_peers(self) -> list:
        pass

    def add_peer(self, name: str) -> None:
        pass

    def del_peer(self, pubkey: str) -> None:
        pass

    def enable_peer(self, pubkey: str) -> None:
        pass

    def disable_peer(self, pubkey: str) -> None:
        pass

    def get_peer_enabled(self, pubkey: str) -> bool:
        pass
