# wg-assistant

Telegram bot for managing WireGuard VPN.

## 🎯 Features

* Add new clients with automatic configuration and QR code generation.
* Manage clients: delete, disable, enable.
* View client status (endpoint, traffic, etc.).
* Register an unlimited number of servers.

## ✅ Supported platforms

* Linux ([default](https://www.wireguard.com) and [AmneziaWG](https://docs.amnezia.org/documentation/amnezia-wg/))
* [RouterOS](https://help.mikrotik.com/docs/display/ROS/WireGuard)

## 🛠 Installation

Before installation, create an account for your bot using [BotFather](https://t.me/BotFather).
You can read more about BotFather [here](https://core.telegram.org/bots/features#botfather).

Also, you need to know your chat ID.
You can find it out using special bots, for example, [userinfobot](https://t.me/userinfobot).

### 🐋 Docker (recommended)

* **Preinstall:** Install [Docker](https://docs.docker.com/engine/install/).
* **Step 1:** Clone the repository and go to the directory with it:
  ```bash
  git clone https://github.com/subs1stem/wg-assistant.git
  cd wg-assistant
  ```
* **Step 2:** Copy and edit the .env file:
  ```bash
  cp .env.example .env
  nano .env
  ```
* **Step 3:** Copy and edit the servers configuration file:
  ```bash
  cp servers.example.json servers.json
  nano servers.json
  ```

> [!IMPORTANT]
> If you don't want to use SSH connection to the Linux host at this stage, go [here](#-local-deployment).

* **Step 4:** Create an image of your bot:
  ```bash
  sudo docker build -t subs1stem/wg-assistant .
  ```
* **Step 5:** Run a container with your image:
  ```bash
  sudo docker run --name wg-assistant --restart unless-stopped -d subs1stem/wg-assistant
  ```
  or mount the configuration files inside the container:
  ```bash
  sudo docker run --name wg-assistant --restart unless-stopped \
  -v ./servers.json:/app/servers.json \
  -v ./.env:/app/.env \
  -d subs1stem/wg-assistant
  ```

## 📦 Local deployment

If you want to deploy the bot on the same host as the WireGuard server and avoid using SSH, you can keep the simplest
configuration:

```json
{
  "MyServer": {
    "type": "Linux",
    "data": {
      "endpoint": "myserver.com"
    }
  }
}
```

After that, you need to build the image with the `LOCAL_DEPLOYMENT=true` argument:

```bash
sudo docker build --build-arg LOCAL_DEPLOYMENT=true -t subs1stem/wg-assistant .
```

Finally, run the container:

```bash
sudo docker run --name wg-assistant \
  --restart unless-stopped \
  --cap-add NET_ADMIN \
  --network host \
  -v /etc/wireguard:/etc/wireguard \
  -d subs1stem/wg-assistant
```
