# wg-assistant

Telegram bot for managing your own WireGuard servers.

## Features 🎯

* Adding new clients with automatic generation of configuration and QR code.
* Managing existing clients: deleting, disabling, enabling.
* View client status (endpoint, traffic, etc.).
* Manage an unlimited number of servers.

## Quick start

```
git clone https://github.com/subs1stem/wg-assistant.git
cd wg-assistant/
chmod +x install.sh
./install.sh
```

Then go to `/etc/wg-assistant/wg-assistant.conf` and edit the config file

Finally, run the docker container:

```
sudo docker run -v /etc/wg-assistant:/etc/wg-assistant --name wg-assistant -d wg-assistant
```
