import json
import os


class ServersFile:
    def __init__(self, filename: str = 'servers.json'):
        self.file_path = os.path.join(os.getcwd(), filename)
        self.servers = None

    def _load_servers(self):
        with open(self.file_path) as f:
            self.servers = json.load(f)

    def get_all_servers(self) -> dict:
        if self.servers is None:
            self._load_servers()
        return self.servers

    def get_server_names(self) -> list:
        if self.servers is None:
            self._load_servers()
        return list(self.servers.keys())

    def get_server_by_name(self, name: str) -> dict:
        if self.servers is None:
            self._load_servers()
        return self.servers.get(name)
