from subprocess import Popen, PIPE
from typing import Tuple, Any

from .base import BaseClient


class LocalClient(BaseClient):
    def execute(self, command: str) -> Tuple[Any, Any, Any]:
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
        stdout, stderr = process.communicate()
        return stdout, stderr, process.returncode

    def get_file_contents(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def put_file_contents(self, path: str, contents: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(contents)
