from datetime import datetime

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

    def get_pubkey(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} public-key')
        return stdout.readline()

    def get_privkey(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} private-key')
        return stdout.readline()

    def get_listen_port(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} listen-port')
        return stdout.readline()

    def get_endpoints(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} endpoints')
        endpoints = {}
        for line in stdout.readlines():
            key, value = line.split()
            endpoints[key] = value
        return endpoints

    def get_allowed_ips(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} allowed-ips')
        allowed_ips = {}
        for line in stdout.readlines():
            key, value = line.split()
            allowed_ips[key] = value
        return allowed_ips

    def get_latest_handshakes(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} latest-handshakes')
        latest_handshakes = {}
        for line in stdout.readlines():
            key, value = line.split()
            latest_handshakes[key] = datetime.fromtimestamp(int(value)).strftime('%d.%m.%Y, %H:%M:%S')
        return latest_handshakes

    def get_transfer(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} transfer')
        transfer = {}
        for line in stdout.readlines():
            key, received, send = line.split()
            transfer[key] = [self.convert_bytes(received), self.convert_bytes(send)]
        return transfer

    def get_peer_names(self):
        _, stdout, _ = self.client.exec_command(f'cat {self.patch_to_conf}')
        config = []
        peer_names = {}
        for line in stdout.readlines():
            config.append(line.strip())
        for i, item in enumerate(config):
            if item.startswith('PublicKey'):
                pubkey = item.split('=', 1)[1].strip()
                name = config[i - 1]
                if name.startswith('#'):
                    name = name.strip(' #')
                else:
                    name = None
                peer_names[pubkey] = name
        return peer_names

    def get_peers(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name}')
        peer_names = self.get_peer_names()
        str_blocks = stdout.read().decode().split('\n\n')
        peers = {}
        for block in str_blocks:
            unit = block.split('\n  ')
            key = unit.pop(0).split(':')[1].strip()
            try:
                peer_name = peer_names[key]
            except KeyError:
                peer_name = key
            peers[peer_name] = None
            inside_dict = {}
            for item in unit:
                inside_key, inside_value = item.split(':', 1)
                inside_dict[inside_key.strip()] = inside_value.strip()
            peers[peer_name] = inside_dict
        return peers

    def get_raw_config(self):
        _, stdout, _ = self.client.exec_command(f'cat {self.patch_to_conf}')
        config = ''
        for line in stdout.readlines():
            config += line
        return config

    def get_wg_status(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name}')
        return bool(stdout.readline())

    def wg_change_state(self, state):
        self.client.exec_command(f'wg-quick {state} {self.wg_interface_name}')

    @staticmethod
    def convert_bytes(bytes_number):
        bytes_number = int(bytes_number)
        tags = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
        i = 0
        double_bytes = bytes_number
        while i < len(tags) and bytes_number >= 1024:
            double_bytes = bytes_number / 1024.0
            i = i + 1
            bytes_number = bytes_number / 1024
        return str(round(double_bytes, 2)) + ' ' + tags[i]


if __name__ == '__main__':
    pass
