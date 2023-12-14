import json
import os


class ServersFileLoader:
    """A class for loading server configurations from a JSON file.

    Attributes:
        file_path (str): The full path to the JSON file containing server configurations.
        servers (dict): A dictionary containing server configurations loaded from the file.
    """

    def __init__(self, filename: str = 'servers.json'):
        """Initialize a new ServersFileLoader instance.

        Args:
           filename (str): The name of the JSON file containing server configurations.
                           Defaults to 'servers.json'.
        """
        self.file_path = os.path.join(os.getcwd(), filename)
        self.servers = None

    def _load_servers(self):
        """Load server configurations from the JSON file into the 'servers' attribute.

        If 'servers' is already loaded, this method does nothing.
        """
        if self.servers is None:
            with open(self.file_path) as f:
                self.servers = json.load(f)

    def get_servers(self) -> dict:
        """Get the loaded server configurations.

        Returns:
            dict: A dictionary containing server configurations.

        Note:
            The server configurations are loaded from the JSON file if not already loaded.
        """
        self._load_servers()
        return self.servers
