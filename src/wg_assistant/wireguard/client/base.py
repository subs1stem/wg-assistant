from abc import ABC, abstractmethod
from typing import Tuple, Any


class BaseClient(ABC):
    """Abstract base class for all clients."""

    @abstractmethod
    def execute(self, command: str) -> Tuple[Any, Any, Any]:
        """Execute a command and return its output.

        Args:
            command (str): The command to execute.

        Returns:
            Tuple[Any, Any, Any]: A tuple containing:

                - stdin (Any): The standard input stream (if applicable).
                - stdout (Any): The standard output stream.
                - stderr (Any): The standard error stream.
        """

    @abstractmethod
    def get_file_contents(self, path: str) -> str:
        """Retrieve the contents of a file.

        Args:
            path (str): The path to the file.

        Returns:
            str: The contents of the file as a string.
        """

    @abstractmethod
    def put_file_contents(self, path: str, contents: str) -> None:
        """Write contents to a file.

        Args:
            path (str): The path to the file.
            contents (str): The contents to write to the file.
        """
