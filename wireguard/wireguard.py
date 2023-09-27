from abc import ABC, abstractmethod


class WireGuard(ABC):
    def __init__(self):
        """"""

    @abstractmethod
    def __del(self):
        """"""

    @abstractmethod
    def reboot_host(self):
        """"""

    @abstractmethod
    def get_config_raw(self):
        """"""

    @abstractmethod
    def get_config(self):
        """"""

    @abstractmethod
    def change_state(self):
        """"""

    @abstractmethod
    def restart(self):
        """"""

    @abstractmethod
    def get_peers(self):
        """"""

    @abstractmethod
    def add_peer(self):
        """"""

    @abstractmethod
    def del_peer(self):
        """"""

    @abstractmethod
    def enable_peer(self):
        """"""

    @abstractmethod
    def disable_peer(self):
        """"""

    @abstractmethod
    def get_peer_enabled(self):
        """"""
