import wgconfig


class Wireguard:
    def __init__(self, path_to_config):
        self.wg_config = wgconfig.WGConfig(path_to_config)
        self.wg_config.read_file()

    def __del__(self):
        self.wg_config.write_file()

    def add_peer(self, pubkey, peer_name):
        self.wg_config.add_peer(pubkey, peer_name)

    def delete_peer(self, pubkey):
        self.wg_config.del_peer(pubkey)

    def enable_peer(self, pubkey):
        self.wg_config.enable_peer(pubkey)

    def disable_peer(self, pubkey):
        self.wg_config.disable_peer(pubkey)

    def get_peer_enabled(self, pubkey):
        self.wg_config.get_peer_enabled(pubkey)
