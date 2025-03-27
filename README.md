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
> If you don't want to use an SSH connection to the Linux host at this stage, go [here](#-local-deployment).

> [!IMPORTANT]
> To use the bot with RouterOS, make sure the port for
> the [API](https://help.mikrotik.com/docs/spaces/ROS/pages/47579160/API) is enabled on your device.

<details>
<summary>💡 Full description of the parameters used in the server configuration file</summary>

```json5
[
  // Parameters of one server are a JSON record.
  // Parameters that have a default value can be omitted.
  {
    // Ensure that different names are used for different servers, or you will get an error.
    "name": "Any name",
    // "Linux" for Linux-based servers or "RouterOS" for MikroTik-based servers.
    // Defaults to "Linux".
    "type": "Linux",
    // "WireGuard" or "AmneziaWG" depending on the protocol being used.
    // Defaults to "WireGuard".
    "protocol": "WireGuard",
    // Path to the WireGuard server configuration file. 
    // Defaults to "/etc/wireguard/wg0.conf" for "WireGuard" protocol.
    // Defaults to "/etc/amnezia/amneziawg/awg0.conf" for "AmneziaWG" protocol.
    "path_to_config": "/etc/wireguard/wg0.conf",
    // Interface name for the WireGuard server.
    // Defaults to "wg0" for "WireGuard" protocol.
    // Defaults to "awg0" for "AmneziaWG" protocol.
    "interface_name": "wg0",
    // Endpoint for peers as an IP address or domain name.
    // By default, the host's external IP address will be used.
    "endpoint": "myserver.com",
    // DNS addresses for peers. Can be a single address or a comma-separated list.
    // By default, the internal address of the server interface will be used.
    "dns": "1.1.1.1, 1.0.0.1",
    // The IP address or domain name of the WireGuard host that the bot will use to connect.
    // If not specified, a local client will be used.
    "server": "192.168.32.1",
    // The port of the WireGuard host that the bot will use to connect.
    // Defaults to 22 (SSH) for "Linux" type.
    // Defaults to 8728 (RouterOS API) for "RouterOS" type.
    "port": 22,
    // Username that the bot will use to connect. Defaults to the current local username.
    "username": "root",
    // Password that the bot will use to connect. Also used for private key decryption.
    // If not specified, private key will be used.
    "password": "toor",
    // The filename, or list of filenames, of optional private key(s)
    // and/or certs to try for authentication.
    // If not specified, the bot will try to use local keyfiles or the SSH agent.
    "key_filename": "/home/user/.ssh/id_ed25519"
  },
  // JSON record for next server.
  {
    // ...
    // ...
    // ...
  }
]
```

</details>

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

If you want to deploy the bot on the same host as the WireGuard server and avoid using SSH, you can do it without the
`servers.json` configuration file, or simplify the configuration by specifying only the `name` parameter:

```json
[
  {
    "name": "My WireGuard"
  }
]
```

or for **AmneziaWG**:

```json
[
  {
    "name": "My AmneziaWG",
    "protocol": "AmneziaWG"
  }
]
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
