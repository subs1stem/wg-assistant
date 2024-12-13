from abc import ABC, abstractmethod


class BaseConfigBuilder(ABC):
    """"""

    @abstractmethod
    def build_client_config(self) -> str:
        pass
