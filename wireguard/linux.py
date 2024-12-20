from functools import wraps
from time import sleep
from typing import Callable, Any, Tuple

from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError, SSHException
from wgconfig import WGConfig

from wireguard.wireguard import WireGuard


class Linux(WireGuard):
    """A class for a WireGuard server deployed on a Linux host."""

    _TMP_CONFIG = '/tmp/wg0.conf'
    _RESTART_DELAY = 3

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str,
            interface_name: str = 'wg0',
            path_to_config: str = '/etc/wireguard/wg0.conf',
    ) -> None:
        """Initialize a new instance of Linux WireGuard client.

        Args:
            server (str): The server address.
            port (int): The port number for the connection.
            username (str): The username for authentication.
            password (str): The password for authentication.
            interface_name (str, optional): The WireGuard interface name. Defaults to 'wg0'.
            path_to_config (str, optional): The path to the WireGuard configuration file.
                Defaults to '/etc/wireguard/wg0.conf'.

        Returns:
            None
        """
        super().__init__(server, port, username, password, interface_name)

        self.path_to_config = path_to_config

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.connect()

        self.wg_config = WGConfig(self._TMP_CONFIG)

    def __del__(self) -> None:
        self.client.close()

    @staticmethod
    def retry_on_ssh_exception(max_retries: int = 3) -> Callable:
        """Decorator for retrying a method in case of ConnectionError.

        Args:
            max_retries (int): The maximum number of retry attempts (default is 3).

        Returns:
            Callable: Decorated function.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                for _ in range(max_retries):
                    try:
                        return func(self, *args, **kwargs)
                    except (SSHException, ConnectionError):
                        self.connect()

            return wrapper

        return decorator

    @retry_on_ssh_exception()
    def _exec_command(self, command: str) -> Tuple[Any, Any, Any]:
        """Execute an SSH command, attempting to reconnect if SSHException is thrown.

        Args:
            command (str): The command to be executed on the remote SSH server.

        Returns:
            Tuple[Any, Any, Any]: A tuple containing stdin, stdout, and stderr streams.
        """
        return self.client.exec_command(command)

    @retry_on_ssh_exception()
    def _download_config(self) -> None:
        """Download the WireGuard server configuration file to the local temporary file.

        Returns:
            None
        """
        self.client.open_sftp().get(self.path_to_config, self._TMP_CONFIG)

    @retry_on_ssh_exception()
    def _upload_config(self) -> None:
        """Upload the local temporary WireGuard configuration file to the remote host.

        Returns:
            None
        """
        self.client.open_sftp().put(self._TMP_CONFIG, self.path_to_config)

    def _generate_key_pair(self) -> Tuple[str, str]:
        """Generate a WireGuard private-public key pair using an SSH connection.

        Returns:
            Tuple[str, str]: A tuple containing the private key and public key strings.
        """
        _, stdout, _ = self._exec_command(f'wg genkey')
        privkey = stdout.readline().strip()

        _, stdout, _ = self._exec_command(f'echo "{privkey}" | wg pubkey')
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

    @staticmethod
    def parse_config_to_dict(config: str) -> dict:
        """Parse a WireGuard server configuration string and convert it into a dictionary.

        Args:
            config (str): The WireGuard server configuration as a string.

        Returns:
            dict: A dictionary representation of the WireGuard server configuration.
        """
        config_dict = {}
        now_section_name = 'Interface'
        now_section_content = {}

        for line in config.splitlines():
            line = line.replace('#!', '').strip()

            if line.startswith('# '):
                config_dict[now_section_name] = now_section_content
                now_section_content = {}
                now_section_name = line.lstrip('# ').rstrip()

            elif line and not line.startswith('['):
                line = line.lstrip('#!')
                key, value = (item.strip() for item in line.split(' = '))
                now_section_content[key] = value

        config_dict[now_section_name] = now_section_content
        return config_dict

    def connect(self) -> None:
        try:
            self.client.connect(
                hostname=self.server,
                username=self.username,
                password=self.password,
                port=self.port
            )
        except (SSHException, NoValidConnectionsError, ConnectionResetError) as e:
            raise ConnectionError(f'Error connecting to WireGuard server host: {e}')

    def reboot_host(self) -> None:
        self._exec_command('reboot')

    def get_config(self, as_dict: bool = False) -> str | dict:
        _, stdout, _ = self._exec_command(f'cat {self.path_to_config}')
        config = ''.join(stdout.readlines())
        return self.parse_config_to_dict(config) if as_dict else config

    def set_wg_enabled(self, enabled: bool) -> None:
        state = 'up' if enabled else 'down'
        self._exec_command(f'wg-quick {state} {self.interface_name}')

    def get_wg_enabled(self) -> bool:
        _, stdout, _ = self._exec_command(f'wg show {self.interface_name}')
        return bool(stdout.readline())

    def get_server_pubkey(self) -> str | None:
        _, stdout, stderr = self._exec_command(f'wg show {self.interface_name} public-key')
        return None if stderr.readline() else stdout.readline().strip()

    def restart(self) -> None:
        self.set_wg_enabled(False)
        sleep(self._RESTART_DELAY)
        self.set_wg_enabled(True)

    def get_peers(self) -> dict:
        _, stdout, stderr = self._exec_command(f'wg show {self.interface_name}')

        if stderr.read().decode():
            return {}

        str_blocks = stdout.read().decode().split('\n\n')

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
        privkey, pubkey = self._generate_key_pair()

        config = self.get_config(as_dict=True)
        server_port = config.get('Interface').get('ListenPort')
        peer_ip = self.get_available_ip(config)

        self.wg_config.add_peer(pubkey, '# ' + name)
        self.wg_config.add_attr(pubkey, 'AllowedIPs', peer_ip)

        client_config = self.build_client_config(
            privkey=privkey,
            address=peer_ip,
            server_pubkey=self.get_server_pubkey(),
            server_ip=self.server,
            server_port=server_port,
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
        section_start_position = self.wg_config.get_sectioninfo(pubkey)[0]
        first_line = self.wg_config.lines[section_start_position]

        # Check if a line is a comment
        if not first_line.startswith('#'):
            return

        self.wg_config.lines[section_start_position] = '# ' + new_name
