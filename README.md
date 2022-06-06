# wg-assistant
Telegram bot for own WireGuard server management

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
