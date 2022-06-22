import time
from datetime import datetime
from ipaddress import ip_interface

import qrcode
from paramiko import SSHClient, AutoAddPolicy

from wireguard.config import Config
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
        return stdout.readline().strip()

    def get_privkey(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} private-key')
        return stdout.readline()

    def get_listen_port(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name} listen-port')
        return stdout.readline().strip()

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
            allowed_ips[key] = value.split('/')[0]
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
        wg_config = []
        peer_names = {}
        for line in stdout.readlines():
            wg_config.append(line.strip())
        for i, item in enumerate(wg_config):
            if item.startswith('PublicKey'):
                pubkey = item.split('=', 1)[1].strip()
                name = wg_config[i - 1]
                if name.startswith('#'):
                    name = name.strip(' #')
                else:
                    name = None
                peer_names[pubkey] = name
        return peer_names

    def get_peers(self):
        if not self.get_wg_status():
            return False
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
        wg_config = ''
        for line in stdout.readlines():
            wg_config += line
        return wg_config

    def get_server_address(self):
        _, stdout, _ = self.client.exec_command(f'cat {self.patch_to_conf}')
        lines = stdout.readlines()
        network = [s for s in lines if 'Address' in s][0].split('=')[1].strip()
        return network

    def get_available_ip(self):
        server_address = self.get_server_address()
        server_ip = format(ip_interface(server_address).ip)
        network = ip_interface(server_address).network
        reserved = list(self.get_allowed_ips().values())
        reserved.append(server_ip)
        hosts_iterator = (host for host in network.hosts() if str(host) not in reserved)
        return next(hosts_iterator)

    def get_wg_status(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.wg_interface_name}')
        return bool(stdout.readline())

    def wg_change_state(self, state):
        self.client.exec_command(f'wg-quick {state} {self.wg_interface_name}')

    def wg_down_up(self):
        self.wg_change_state('down')
        time.sleep(1)
        self.wg_change_state('up')

    def add_peer(self, peer_name):
        _, stdout, _ = self.client.exec_command(f'wg genkey')
        privkey = stdout.readline().strip()
        _, stdout, _ = self.client.exec_command(f'echo "{privkey}" | wg pubkey')
        pubkey = stdout.readline().strip()
        server_pubkey = self.get_pubkey()
        peer_ip = f'{self.get_available_ip()}/32'
        server_ip = format(ip_interface(self.get_server_address()).ip)
        server_port = self.get_listen_port()
        text = '[Peer]\n' \
               f'# {peer_name}\n' \
               f'PublicKey = {pubkey}\n' \
               f'AllowedIPs = {peer_ip}\n'
        self.client.exec_command(f'echo "{text}" >> {self.patch_to_conf}')
        self.wg_down_up()
        wg_config = self.generate_client_config(privkey, peer_ip, server_ip, server_pubkey, self.host, server_port)
        qr = self.make_qr(wg_config)
        return qr, wg_config

    def is_peer_disabled(self, peer_name):
        pass

    def delete_peer(self, peer_name):
        pass

    def disable_peer(self, peer_name):
        Config(self.get_raw_config()).parse_config()

    @staticmethod
    def generate_client_config(privkey, address, dns, pubkey, server_ip, server_port):
        wg_config = '[Interface]\n' \
                 f'PrivateKey = {privkey}\n' \
                 f'Address = {address}\n' \
                 f'DNS = {dns}\n\n' \
                 '[Peer]\n' \
                 f'PublicKey = {pubkey}\n' \
                 'AllowedIPs = 0.0.0.0/0\n' \
                 f'Endpoint = {server_ip}:{server_port}\n' \
                 'PersistentKeepalive = 30'
        return wg_config

    @staticmethod
    def make_qr(text):
        img = qrcode.make(text)
        return img

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
