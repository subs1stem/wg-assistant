from abc import ABC, abstractmethod
from typing import Tuple, Any


class BaseExecutor(ABC):
    """Abstract base class for all executors."""

    @abstractmethod
    def exec_command(self, command: str) -> Tuple[Any, Any, Any]:
        """Execute a command and return its output.

        Args:
            command (str): The command to execute.

        Returns:
            Tuple[Any, Any, Any]: A tuple containing:

                - stdin (Any): The standard input stream (if applicable).
                - stdout (Any): The standard output stream.
                - stderr (Any): The standard error stream.
        """
