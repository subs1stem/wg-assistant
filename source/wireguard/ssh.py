from paramiko import SSHClient, AutoAddPolicy

from settings import *


class SSH:
    def __init__(self):
        self.host = SSH_HOST
        self.user = SSH_USER
        self.secret = SSH_SECRET
        self.port = SSH_PORT
        self.patch_to_conf = PATH_TO_WG_CONF
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

    def get_peer_name(self, pub_key):
        config = self.get_config().split('\n')
        return config

    def get_peers(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name}')
        return stdout.readlines()

    def get_config(self):
        _, stdout, _ = self.client.exec_command(f'cat {self.patch_to_conf}')
        config = []
        for line in stdout.readlines():
            line = line.replace('\n', '')
            if not line:
                continue
            config.append(line)
        return config


if __name__ == '__main__':
    print(SSH().get_config())
