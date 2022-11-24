import time

from paramiko import SSHClient, AutoAddPolicy
from wgconfig import WGConfig

from settings import *


class SSH:
    path_to_tmp_config = '/tmp/wg0.conf'
    wg_config = WGConfig(path_to_tmp_config)

    def __init__(self):
        self.host = SSH_HOST
        self.user = SSH_USER
        self.secret = SSH_SECRET
        self.port = SSH_PORT
        self.path_to_config = PATH_TO_WG_CONFIG
        self.wg_interface_name = WG_INTERFACE_NAME
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(hostname=self.host,
                            username=self.user,
                            password=self.secret,
                            port=self.port,
                            timeout=5)

    def __del__(self):
        self.client.close()

    def ping(self):
        _, stdout, _ = self.client.exec_command('ping -c 1 8.8.8.8', timeout=1)
        return bool(stdout.read())

    def reboot(self):
        self.client.exec_command('reboot')

    def get_raw_config(self):
        _, stdout, _ = self.client.exec_command(f'cat {self.path_to_config}')
        return ''.join(stdout.readlines())

    def get_wg_status(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name}')
        return bool(stdout.readline())

    def wg_change_state(self, state):
        self.client.exec_command(f'wg-quick {state} {self.wg_interface_name}')

    def wg_down_up(self):
        self.wg_change_state('down')
        time.sleep(1)
        self.wg_change_state('up')

    def download_config(self):
        self.client.open_sftp().get(self.path_to_config, self.path_to_tmp_config)

    def upload_config(self):
        self.client.open_sftp().put(self.path_to_tmp_config, self.path_to_config)

    def add_peer(self, peer_name):
        self.download_config()
        self.wg_config.read_file()

    def delete_peer(self, pubkey):
        self.download_config()
        self.wg_config.read_file()
        self.wg_config.del_peer(pubkey)
        self.wg_config.write_file()
        self.upload_config()
        self.wg_down_up()

    def enable_peer(self, pubkey):
        self.download_config()
        self.wg_config.read_file()
        self.wg_config.enable_peer(pubkey)
        self.wg_config.write_file()
        self.upload_config()
        self.wg_down_up()

    def disable_peer(self, pubkey):
        self.download_config()
        self.wg_config.read_file()
        self.wg_config.disable_peer(pubkey)
        self.wg_config.write_file()
        self.upload_config()
        self.wg_down_up()

    def get_peer_enabled(self, pubkey):
        self.download_config()
        self.wg_config.read_file()
        return self.wg_config.get_peer_enabled(pubkey)


if __name__ == '__main__':
    ssh = SSH()
    ssh.delete_peer('U0cwkQJMZlUPtNQ7n1FpXoAQZ5rbCJ6gzUuW+9yqSy0=')
