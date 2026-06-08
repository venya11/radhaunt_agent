# RadHaunt_Agent

A lightweight, adaptive Python-based remote administration agent, controlled entirely via Telegram.

---

## Features & Use Cases

What can you use **RadHaunt_Agent** for?

* **Remote System Administration:** Manage your Linux machine from your phone while away. Check server statuses, restart services or run scripts.
* **RedTeam / Pentesting Backdoor:** Functions as a stealthy C2 (Command and Control) agent. 
  * 🔒 **No open ports needed:** It initiates outbound HTTPS connections to Telegram servers (Port 443), easily bypassing strict firewalls.
  * 🌐 **Zero VPS hosting costs:** Uses Telegram infrastructure as the backend, eliminating the need to buy and set up your own C2 server.
* **On-Demand Monitoring:** Instantly request a screenshot of the active desktop. The agent automatically detects the display server (`X11` or `Wayland`) and desktop environment (`Cinnamon`, `GNOME`, `KDE`, `Hyprland`, `Sway`) to capture a flawless image.
* **Smart Sudo Integration:** Seamlessly handles `sudo` commands by securely piping passwords, while automatically filtering out annoying internal system prompts.

---

## 🌐 Supported Environments & Distros

The agent automatically adapts to your system configuration and has been tested across major Linux distributions:

| Distribution | Display Server | Tested Desktop Environments / WMs |
| :--- | :--- | :--- |
| **Linux Mint / Ubuntu / Debian** | X11 / Wayland | Cinnamon, GNOME, XFCE |
| **Kali Linux** | X11 | XFCE |
| **Arch Linux / Manjaro** | X11 / Wayland | Hyprland, Sway, KDE Plasma |
| **Fedora** | Wayland | GNOME, KDE |

*Note: For Wayland-based environments, ensuring `ydotool` is installed and its background daemon (`ydotoold`) is running may be required for simulated keystrokes (`type` command).*

---

## Installation Guide

### 1. Clone the Repository and Install Dependencies
```bash
git clone https://github.com/venya11/radhaunt_agent.git
cd radhaunt_agent
```
Install the required display utilities based on your package manager:
Ubuntu / Debian / Linux Mint:
```bash
    sudo apt update && sudo apt install xdotool ydotool -y
```
Arch Linux / Manjaro:
```bash
    sudo pacman -S --noconfirm xdotool ydotool
```
Fedora:
```bash
    sudo dnf install xdotool ydotool -y
```
### 2. Set Up a Virtual Environment and install requirements

Create an isolated environment and install the required dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. Configuration

Open radhaunt_agent.py in any text editor and fill in your credentials at the top of the file:
```python
API_TOKEN = ''                                 # Get it from @BotFather
ADMIN_ID =                                     # Your personal Telegram User ID
ADMIN_USER_SYSTEM = ''                         # Your Linux OS username
ADMIN_USER_SUDO_PASSWD = ''                    # Your sudo password for root actions
```
Persistent Autostart Setup

Choose one of the methods below based on your Linux initialization system or setup preference:
Method A: Systemd Service (Recommended for standard distros like Mint, Ubuntu, Arch, Kali)

Create a new service file:
```bash
sudo nano /etc/systemd/system/radhaunt_agent.service
```
Paste the following configuration (replace {YOUR_USER} and {PATH_TO_PROJECT} with your actual data):
```bash
[Unit]
Description=RadHaunt Telegram Remote Control Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User={YOUR_USER}
ExecStart=/home/{YOUR_USER}/{PATH_TO_PROJECT}/venv/bin/python /home/{YOUR_USER}/{PATH_TO_PROJECT}/radhaunt_agent.py
WorkingDirectory=/home/{YOUR_USER}/{PATH_TO_PROJECT}/
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable radhaunt_agent.service
sudo systemctl start radhaunt_agent.service
```
### Method B: XDG Autostart (For non-systemd distros like Artix, Void, Gentoo or Desktop-only execution)

Create the autostart directory if it doesn't exist:
```bash
mkdir -p ~/.config/autostart
```
Create the desktop shortcut entry:
```bash
nano ~/.config/autostart/radhaunt_agent.desktop
```
Paste the following text into the file (update the execution path):
```bash
[Desktop Entry]
Type=Application
Name=RadHaunt Telegram Agent
Comment=Remote control backdoor agent
Exec=/home/{YOUR_USER}/{PATH_TO_PROJECT}/venv/bin/python /home/{YOUR_USER}/{PATH_TO_PROJECT}/radhaunt_agent.py
Terminal=false
X-GNOME-Autostart-enabled=true
```
### 🎯 Verification

Open Telegram and go to your bot's chat.
Send the /start command.
If everything is configured correctly, the bot will respond with:
    "🤖 Hello! Agent has been started. Waiting for shell commands, or enter '/help'."
