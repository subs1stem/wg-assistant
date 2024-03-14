# wg-assistant

Telegram bot for managing WireGuard VPN.

## 🎯 Features

* Adding new clients with automatic generation of configuration and QR code.
* Managing existing clients: deleting, disabling, enabling.
* View client status (endpoint, traffic, etc.).
* Manage an unlimited number of servers.

## ✅ Supported

* [Linux](https://www.wireguard.com)

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
* **Step 4:** Create an image of your bot:
  ```bash
  sudo docker build -t wg-assistant .
  ```
* **Step 5:** Run a container with your image:
  ```bash
  sudo docker run --name wg-assistant --restart unless-stopped -d wg-assistant
  ```

### 🐍 venv

...
