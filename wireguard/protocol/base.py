from abc import ABC, abstractmethod


class BaseProtocol(ABC):
    """"""

    @abstractmethod
    def get_client_config(self) -> str:
        pass
