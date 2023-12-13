import json
import os


class ServersFileLoader:
    def __init__(self, filename: str = 'servers.json'):
        self.file_path = os.path.join(os.getcwd(), filename)
        self.servers = None

    def _load_servers(self):
        if self.servers is None:
            with open(self.file_path) as f:
                self.servers = json.load(f)

    def get_servers(self) -> dict:
        self._load_servers()
        return self.servers
