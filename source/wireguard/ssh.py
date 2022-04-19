from paramiko import SSHClient, AutoAddPolicy

from settings import *


class SSH:
    def __init__(self):
        self.host = SSH_HOST
        self.user = SSH_USER
        self.secret = SSH_SECRET
        self.port = SSH_PORT
        self.patch_to_conf = PATH_TO_WG_CONF
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

    def get_raw_config(self):
        _, stdout, _ = self.client.exec_command(f'cat {self.patch_to_conf}')
        config = ''
        for line in stdout.readlines():
            config += line
        return config


if __name__ == '__main__':
    pass
