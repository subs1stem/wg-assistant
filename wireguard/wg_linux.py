from asyncio import sleep

from paramiko import SSHClient, AutoAddPolicy

from wireguard.wg_interface import WGInterface


class WGLinux(WGInterface):

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str,
            config: str = '/etc/wireguard/wg0.conf',
            interface: str = 'wg0',
    ) -> None:
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.config = config
        self.interface = interface
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def __del__(self):
        self.client.close()

    def connect(self) -> None:
        try:
            self.client.connect(hostname=self.server,
                                username=self.username,
                                password=self.password,
                                port=self.port)
        except Exception:
            raise ConnectionError('Error connecting to WireGuard server')

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
