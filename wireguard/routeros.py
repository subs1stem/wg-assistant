import logging
from functools import wraps
from typing import Any, Callable

from humanize import naturalsize
from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

from wireguard.protocol.base import BaseProtocol
from wireguard.wireguard import WireGuard


class RouterOS(WireGuard):
    """Class for WireGuard server deployed on RouterOS."""

    def __init__(
            self,
            server: str,
            port: int,
            username: str,
            password: str,
            protocol: BaseProtocol,
            endpoint: str,
            interface_name: str = 'wireguard1',
    ) -> None:
        """Initialize a new instance of the RouterOS WireGuard client.

        Args:
            server (str): The server address.
            port (int): The port number for the connection.
            username (str): The username for authentication.
            password (str): The password for authentication.
            protocol (BaseProtocol): The WireGuard protocol.
            endpoint (str): The WireGuard server endpoint.
            interface_name (str, optional): The WireGuard interface name. Default is ``wireguard1``.

        Returns:
            None
        """
        super().__init__(protocol, endpoint, interface_name)

        self.server = server
        self.port = port
        self.username = username
        self.password = password

        self.connection = None
        self.api = None

        self.connect()

    def __del__(self):
        self.connection.disconnect()

    @staticmethod
    def _exception_handler(func: Callable) -> Callable:
        """Decorator to handle RouterOS API connection errors.
        Reconnects and retries the function once if a connection error occurs.

        Args:
            func (Callable): The function that might raise a connection error.

        Returns:
            Callable: A wrapped function that retries once after reconnecting.
        """

        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            try:
                return func(self, *args, **kwargs)
            except RouterOsApiConnectionError:
                logging.warning('RouterOS API connection error, reconnecting...')
                self.connect()
                return func(self, *args, **kwargs)
            except Exception as e:
                logging.exception(f'An unexpected error occurred: {e}')

        return wrapper

    @staticmethod
    def _format_config_as_string(config: dict) -> str:
        """Format the WireGuard configuration dictionary as a string.

        Args:
            config (dict): The WireGuard configuration dictionary.

        Returns:
            str: The WireGuard configuration as a string, ending with a newline.
        """
        lines = ['[Interface]']
        lines.extend(f'{key} = {value}' for key, value in config['Interface'].items())

        for peer_name, peer_config in config.items():
            if peer_name != 'Interface':
                lines.append(f'\n# {peer_name}\n[Peer]')
                lines.extend(f'{key} = {value}' for key, value in peer_config.items())

        return '\n'.join(lines) + '\n'

    @_exception_handler
    def _get_interface(self) -> dict[str, Any] | None:
        """Retrieve the WireGuard interface details by its name.

        Returns:
            dict[str, Any] | None: A dictionary containing the interface details if found, otherwise None.
        """
        interface = self.api.get_resource('/interface/wireguard').get(name=self.interface_name)
        return interface[0] if interface else None

    @_exception_handler
    def _get_peer(self, pubkey: str) -> dict[str, Any] | None:
        """Retrieve the WireGuard peer details by its public key.

        Args:
            pubkey (str): The public key of the peer.

        Returns:
            dict[str, Any] | None: A dictionary containing the peer details if found, otherwise None.
        """
        peer = self.api.get_resource('/interface/wireguard/peers').get(public_key=pubkey)
        return peer[0] if peer else None

    def connect(self) -> None:
        self.connection = RouterOsApiPool(
            host=self.server,
            username=self.username,
            password=self.password,
            port=self.port,
            plaintext_login=True,
        )

        self.connection.set_timeout(5)

        try:
            self.api = self.connection.get_api()
        except RouterOsApiConnectionError as e:
            raise ConnectionError(f'Error connecting to RouterOS API: {e}')

    @_exception_handler
    def reboot_host(self) -> None:
        self.api.get_binary_resource('/').call('system/reboot')

    @_exception_handler
    def get_config(self, as_dict: bool = False) -> str | dict:
        interface = self._get_interface()
        address = self.api.get_resource('/ip/address').get(interface=self.interface_name)[0]

        config = {
            'Interface': {
                'PrivateKey': interface.get('private-key'),
                'ListenPort': interface.get('listen-port'),
                'Address': address.get('address'),
            }
        }

        peers = self.api.get_resource('/interface/wireguard/peers').get(interface=self.interface_name)

        for peer in peers:
            peer_name = peer.get('name')
            config[peer_name] = {
                'PublicKey': peer.get('public-key'),
                'AllowedIPs': peer.get('allowed-address'),
            }

        return config if as_dict else self._format_config_as_string(config)

    @_exception_handler
    def set_wg_enabled(self, enabled: bool) -> None:
        interface = self._get_interface()
        if interface:
            self.api.get_resource('/interface/wireguard').set(
                id=interface['id'],
                disabled='no' if enabled else 'yes'
            )

    def get_wg_enabled(self) -> bool:
        interface = self._get_interface()
        return bool(interface and interface.get('disabled') == 'false')

    def get_server_pubkey(self) -> str | None:
        interface = self._get_interface()
        if interface:
            return interface.get('public-key')
        return None

    @_exception_handler
    def restart(self) -> None:
        interface = self._get_interface()
        if interface:
            resource = self.api.get_resource('/interface/wireguard')
            resource.set(id=interface['id'], disabled='yes')
            resource.set(id=interface['id'], disabled='no')

    @_exception_handler
    def get_peers(self) -> dict:
        raw_peers = self.api.get_resource('/interface/wireguard/peers').get(interface=self.interface_name)

        return {
            peer['name']: {
                'endpoint': f'{peer.get('current-endpoint-address')}:{peer.get('current-endpoint-port')}',
                'allowed ips': peer.get('allowed-address'),
                'latest handshake': peer.get('last-handshake'),
                'transfer': f'{naturalsize(peer.get('rx', 0), True)} , {naturalsize(peer.get('tx', 0), True)}',
            }
            for peer in raw_peers
        }

    @_exception_handler
    def add_peer(self, name: str) -> str:
        server_config = self.get_config(as_dict=True)
        interface = self._get_interface()

        peers_resource = self.api.get_resource('/interface/wireguard/peers')

        peers_resource.add(
            name=name,
            interface=self.interface_name,
            private_key='auto',
            allowed_address=self.get_available_ip(server_config),
        )

        peer = peers_resource.get(name=name)[0]

        client_config = self.protocol.build_client_config(
            privkey=peer.get('private-key'),
            address=peer.get('allowed-address'),
            server_pubkey=self.get_server_pubkey(),
            endpoint=self.endpoint,
            server_port=interface.get('listen-port'),
            server_config=server_config,
        )

        return client_config

    @_exception_handler
    def delete_peer(self, pubkey: str) -> None:
        peer = self._get_peer(pubkey)
        if peer:
            self.api.get_resource('/interface/wireguard/peers').remove(id=peer['id'])

    @_exception_handler
    def set_peer_enabled(self, pubkey: str, enabled: bool) -> None:
        peer = self._get_peer(pubkey)
        if peer:
            self.api.get_resource('/interface/wireguard/peers').set(
                id=peer['id'],
                disabled='no' if enabled else 'yes'
            )

    def get_peer_enabled(self, pubkey: str) -> bool:
        peer = self._get_peer(pubkey)
        if peer:
            return peer.get('disabled') == 'false'
        return False

    @_exception_handler
    def rename_peer(self, pubkey: str, new_name: str) -> None:
        peer = self._get_peer(pubkey)
        if peer:
            self.api.get_resource('/interface/wireguard/peers').set(
                id=peer['id'],
                name=new_name
            )
