import configparser
import os
import sys

ROOT_DIR = sys.path[1]

path = '/etc/wg-assistant/wg-assistant.conf'

config = configparser.ConfigParser()

if os.path.exists(path):
    config.read(path)
else:
    config.read(ROOT_DIR + '/config/wg-assistant.conf')

BOT_TOKEN = str(config['BOT']['BotToken'])
ADMIN_IDs = list(map(int, config['BOT']['AdminIDs'].split()))
SSH_HOST = str(config['WIREGUARD']['Host'])
SSH_USER = str(config['WIREGUARD']['User'])
SSH_SECRET = str(config['WIREGUARD']['Password'])
SSH_PORT = int(config['WIREGUARD']['Port'])
PATH_TO_WG_CONF = str(config['WIREGUARD']['PathToConfig'])
WG_INTERFACE_NAME = str(config['WIREGUARD']['Interface'])
