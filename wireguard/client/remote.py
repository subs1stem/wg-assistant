from functools import wraps
from typing import Tuple, Any, Callable

from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException, NoValidConnectionsError

from .base import BaseClient


class RemoteClient(BaseClient):
    """Class that provides a client for remote interaction with a host."""

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str,
    ) -> None:
        self.server = server
        self.port = port
        self.username = username
        self.password = password

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.connect()

    def __del__(self) -> None:
        self.client.close()

    @staticmethod
    def _retry_on_ssh_exception(max_retries: int = 3) -> Callable:
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

    def connect(self) -> None:
        """Connect to the WireGuard server.

        Returns:
            None

        Raises:
            ConnectionError: If the connection to the WireGuard server host fails.
        """
        try:
            self.client.connect(
                hostname=self.server,
                username=self.username,
                password=self.password,
                port=self.port
            )
        except (SSHException, NoValidConnectionsError, ConnectionResetError) as e:
            raise ConnectionError(f'Error connecting to WireGuard server host: {e}')

    @_retry_on_ssh_exception()
    def execute(self, command: str) -> Tuple[Any, Any, Any]:
        return self.client.exec_command(command)

    @_retry_on_ssh_exception()
    def get_file_contents(self, path: str) -> str:
        sftp = self.client.open_sftp()
        with sftp.file(path, mode='r') as f:
            return f.read().decode()

    @_retry_on_ssh_exception()
    def put_file_contents(self, path: str, content: str) -> None:
        sftp = self.client.open_sftp()
        with sftp.file(path, mode='w') as f:
            f.write(content)
