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

> [!TIP]
> If you want to use an SSH key instead of a password to access your Linux server (recommended), the value in the
> `password` field can be used as a passphrase to decrypt the private key. You can remove this field from the
> configuration if you do not use a passphrase.

> [!IMPORTANT]
> If you don't want to use an SSH connection to the Linux host at this stage, go [here](#-local-deployment).

> [!IMPORTANT]
> To use the bot with RouterOS, make sure the port for
> the [API](https://help.mikrotik.com/docs/spaces/ROS/pages/47579160/API) is enabled on your device.

* **Step 4:** Create an image of your bot:
  ```bash
  sudo docker build -t subs1stem/wg-assistant .
  ```
* **Step 5:** Run a container with your image:
  ```bash
  sudo docker run --name wg-assistant --restart unless-stopped -d subs1stem/wg-assistant
  ```
  ⚠️ If an SSH key is used, it must be mounted inside the container:
  ```bash
  sudo docker run --name wg-assistant --restart unless-stopped \
  -v ~/.ssh/id_ed25519:/root/.ssh/id_ed25519:ro \
  -d subs1stem/wg-assistant
  ```
  Optionally, mount the bot's configuration files into the container:
  ```bash
  sudo docker run --name wg-assistant --restart unless-stopped \
  -v ./servers.json:/app/servers.json:ro \
  -v ./.env:/app/.env:ro \
  -d subs1stem/wg-assistant
  ```

## 📦 Local deployment

If you want to deploy the bot on the same host as the WireGuard server and avoid using SSH, you can keep the simplest
configuration without credentials:

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

or for **AmneziaWG**:

```json
{
  "MyServer": {
    "type": "Linux",
    "protocol": "AmneziaWG",
    "data": {
      "interface_name": "awg0",
      "endpoint": "myserver.com",
      "path_to_config": "/etc/amnezia/amneziawg/awg0.conf"
    }
  }
}
```

After that, you need to build the image with the argument `LOCAL_DEPLOYMENT_WG=true` or `LOCAL_DEPLOYMENT_AWG=true`
depending on the protocol you are using. This will install the necessary utilities inside the container.

For **WireGuard**:

```bash
sudo docker build --build-arg LOCAL_DEPLOYMENT_WG=true --build-arg -t subs1stem/wg-assistant .
```

For **AmneziaWG**:

```bash
sudo docker build --build-arg LOCAL_DEPLOYMENT_AWG=true --build-arg -t subs1stem/wg-assistant .
```

Or use both arguments if you have both VPNs on your server:

```bash
sudo docker build --build-arg LOCAL_DEPLOYMENT_WG=true --build-arg LOCAL_DEPLOYMENT_AWG=true -t subs1stem/wg-assistant .
```

Finally, run the container with the server configuration directories mounted.

For **WireGuard**:

```bash
sudo docker run --name wg-assistant \
  --restart unless-stopped \
  --cap-add NET_ADMIN \
  --network host \
  -v /etc/wireguard:/etc/wireguard \
  -d subs1stem/wg-assistant
```

For **AmneziaWG**:

```bash
sudo docker run --name wg-assistant \
  --restart unless-stopped \
  --cap-add NET_ADMIN \
  --network host \
  -v /etc/amnezia/amneziawg:/etc/amnezia/amneziawg \
  -d subs1stem/wg-assistant
```

For both:

```bash
sudo docker run --name wg-assistant \
  --restart unless-stopped \
  --cap-add NET_ADMIN \
  --network host \
  -v /etc/wireguard:/etc/wireguard \
  -v /etc/amnezia/amneziawg:/etc/amnezia/amneziawg \
  -d subs1stem/wg-assistant
```
