import time
from ipaddress import ip_interface

import qrcode
from paramiko import SSHClient, AutoAddPolicy
from wgconfig import WGConfig


class SSH:
    path_to_tmp_config = '/tmp/wg0.conf'

    def __init__(self, host, port, username, password, config='/etc/wireguard/wg0.conf', interface='wg0'):
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.config = config
        self.interface = interface
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

        try:
            self.client.connect(hostname=self.host,
                                username=self.username,
                                password=self.password,
                                port=self.port)
        except Exception:
            raise ConnectionError('Error connecting to WireGuard server')

    def __del__(self):
        self.client.close()

    def ping(self):
        _, stdout, _ = self.client.exec_command('ping -c 1 8.8.8.8', timeout=1)
        return bool(stdout.read())

    def reboot(self):
        self.client.exec_command('reboot')

    def get_raw_config(self):
        _, stdout, _ = self.client.exec_command(f'cat {self.config}')
        return ''.join(stdout.readlines())

    def get_wg_status(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.interface}')
        return bool(stdout.readline())

    def wg_change_state(self, state):
        self.client.exec_command(f'wg-quick {state} {self.interface}')

    def wg_down_up(self):
        self.wg_change_state('down')
        time.sleep(3)
        self.wg_change_state('up')

    def download_config(self):
        self.client.open_sftp().get(self.config, self.path_to_tmp_config)

    def upload_config(self):
        self.client.open_sftp().put(self.path_to_tmp_config, self.config)

    def get_server_pubkey(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.interface} public-key')
        return stdout.readline().strip()

    def get_server_port(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.interface} listen-port')
        return stdout.readline().strip()

    def get_server_address(self):
        _, stdout, _ = self.client.exec_command(f'cat {self.config}')
        lines = stdout.readlines()
        network = [s for s in lines if 'Address' in s][0].split('=')[1].strip()
        return network

    def get_allowed_ips(self):
        _, stdout, _ = self.client.exec_command(f'wg show {self.interface} allowed-ips')
        allowed_ips = {}
        for line in stdout.readlines():
            key, value = line.split()
            allowed_ips[key] = value.split('/')[0]
        return allowed_ips

    def get_next_available_ip(self):
        server_address = self.get_server_address()
        server_ip = format(ip_interface(server_address).ip)
        network = ip_interface(server_address).network
        reserved = list(self.get_allowed_ips().values())
        reserved.append(server_ip)
        hosts_iterator = (host for host in network.hosts() if str(host) not in reserved)
        return next(hosts_iterator)

    def get_peer_names(self):
        self.download_config()
        wg_config = WGConfig(self.path_to_tmp_config)
        wg_config.read_file()
        peers = wg_config.peers
        peer_names = {}
        for peer in peers:
            name = None
            for item in peers[peer]['_rawdata']:
                item = item.replace('#!', '').strip()
                if item.startswith('#'):
                    name = item.replace('#', '').strip()
            peer_names[peer] = name
        return peer_names

    def get_peers(self):
        if not self.get_wg_status():
            return False
        _, stdout, _ = self.client.exec_command(f'wg show {self.interface}')
        peer_names = self.get_peer_names()
        str_blocks = stdout.read().decode().split('\n\n')
        peers = {}
        for block in str_blocks:
            unit = block.split('\n  ')
            key = unit.pop(0).split(':')[1].strip()
            if key == self.interface:
                continue
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

    def add_peer(self, peer_name):
        _, stdout, _ = self.client.exec_command(f'wg genkey')
        client_privkey = stdout.readline().strip()
        _, stdout, _ = self.client.exec_command(f'echo "{client_privkey}" | wg pubkey')
        client_pubkey = stdout.readline().strip()
        server_pubkey = self.get_server_pubkey()
        peer_ip = f'{self.get_next_available_ip()}/32'
        server_port = self.get_server_port()
        self.download_config()
        wg_config = WGConfig(self.path_to_tmp_config)
        wg_config.read_file()
        wg_config.add_peer(client_pubkey, '# ' + peer_name)
        wg_config.add_attr(client_pubkey, 'AllowedIPs', peer_ip)
        wg_config.write_file()
        self.upload_config()
        self.wg_down_up()
        wg_config = self.generate_client_config(client_privkey, peer_ip, server_pubkey, self.host, server_port)
        qr = qrcode.make(wg_config)
        return qr, wg_config

    def delete_peer(self, pubkey):
        self.download_config()
        wg_config = WGConfig(self.path_to_tmp_config)
        wg_config.read_file()
        wg_config.del_peer(pubkey)
        wg_config.write_file()
        self.upload_config()
        self.wg_down_up()

    def enable_peer(self, pubkey):
        self.download_config()
        wg_config = WGConfig(self.path_to_tmp_config)
        wg_config.read_file()
        wg_config.enable_peer(pubkey)
        wg_config.write_file()
        self.upload_config()
        self.wg_down_up()

    def disable_peer(self, pubkey):
        self.download_config()
        wg_config = WGConfig(self.path_to_tmp_config)
        wg_config.read_file()
        wg_config.disable_peer(pubkey)
        wg_config.write_file()
        self.upload_config()
        self.wg_down_up()

    def get_peer_enabled(self, pubkey):
        self.download_config()
        wg_config = WGConfig(self.path_to_tmp_config)
        wg_config.read_file()
        return wg_config.get_peer_enabled(pubkey)

    @staticmethod
    def generate_client_config(privkey, address, pubkey, server_ip, server_port):
        wg_config = '[Interface]\n' \
                    f'PrivateKey = {privkey}\n' \
                    f'Address = {address}\n' \
                    f'DNS = 8.8.8.8\n\n' \
                    '[Peer]\n' \
                    f'PublicKey = {pubkey}\n' \
                    'AllowedIPs = 0.0.0.0/0\n' \
                    f'Endpoint = {server_ip}:{server_port}\n' \
                    'PersistentKeepalive = 30'
        return wg_config


if __name__ == '__main__':
    pass
