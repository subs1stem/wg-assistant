from wireguard.wireguard import WireGuard


class Mikrotik(WireGuard):

    def connect(self) -> None:
        pass

    def reboot_host(self) -> None:
        pass

    def get_config(self) -> str:
        pass

    def set_wg_enabled(self, enabled: bool) -> None:
        pass

    def restart(self) -> None:
        pass

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
