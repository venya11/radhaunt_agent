# RadHaunt_Agent

**A lightweight, adaptive Python-based remote administration tool (RAT/agent), controlled entirely via Telegram.**

**⚠️ Disclaimer: This tool is intended for legitimate system administration and authorized security testing only. The user is solely responsible for ensuring compliance with all applicable laws and regulations. Use only on systems you own or have explicit permission to access.**

---

## 📌 Features

- **Remote Administration Tool (RAT)** - Execute shell commands, manage services, run scripts
- **RedTeam / Pentesting C2 Agent** - No open ports, uses Telegram API (port 443), zero VPS cost
- **On-Demand Monitoring** - Instant screenshots with auto-detection of X11/Wayland and DE
- **Smart Sudo Integration** - Automatic password piping, filters internal prompts
- **Network Security Tools** - Traffic stats, connections, open ports, suspicious connections, nmap scanning

---

## 🌐 Supported Environments

| Distribution | Display Server | Desktop Environments / WMs | Status |
| :--- | :--- | :--- | :---: |
| **Ubuntu 20.04+** | X11 / Wayland | GNOME, Unity, XFCE, KDE | ✅ |
| **Linux Mint 20+** | X11 / Wayland | Cinnamon, MATE, XFCE | ✅ |
| **Debian 11+** | X11 / Wayland | GNOME, KDE, XFCE | ✅ |
| **Kali Linux** | X11 | XFCE, GNOME | ✅ |
| **Arch Linux** | X11 / Wayland | All (Hyprland, Sway, GNOME, KDE, i3, etc.) | ✅ |
| **Manjaro** | X11 / Wayland | GNOME, KDE, XFCE, Hyprland, Sway | ✅ |
| **Fedora 36+** | Wayland / X11 | GNOME, KDE, XFCE | ✅ |
| **openSUSE** | Wayland / X11 | GNOME, KDE | ✅ |
| **Pop!_OS** | X11 / Wayland | GNOME (COSMIC) | ✅ |
| **CentOS/RHEL 8+** | X11 | GNOME, KDE | ✅ |

### ⚠️ Wayland Limitations & Known Issues

Due to Wayland's strict security model and window isolation, some graphical features (`Screenshot`, `Keyboard`, `Type`) may behave unexpectedly or require manual configuration:
- **GNOME / KDE (Wayland):** Native tools like `gnome-screenshot` or `xdotool` are heavily restricted. 
- **Workaround:** For 100% stable coverage of all GUI features, it is **highly recommended to switch your desktop session to Xorg (X11)** via your distro's login screen display manager (click the gear icon ⚙️ before entering your password and select *GNOME on Xorg* or *Plasma X11*).

### X11 Support

| DE/WM | Screenshot | Keyboard | Status |
| :--- | :--- | :--- | :---: |
| GNOME/KDE/XFCE | `scrot` / `xfce4-screenshooter` | `xdotool` | ✅ |
| Cinnamon/MATE | `gnome-screenshot` / `scrot` | `xdotool` | ✅ |
| i3/Awesome/Openbox | `scrot` | `xdotool` | ✅ |

---

## 📦 Dependencies

### Python Packages

```txt
pyTelegramBotAPI==4.13.0
psutil==5.9.5
```
Install:

```bash
pip install -r requirements.txt
```

---

### System Dependencies

#### Screenshot Utilities

| Distro | X11 | Wayland |
| :--- | :--- | :--- |
| Debian/Ubuntu | `sudo apt install scrot xfce4-screenshooter` | `sudo apt install gnome-screenshot spectacle grim` |
| Arch/Manjaro | `sudo pacman -S scrot xfce4-screenshooter` | `sudo pacman -S gnome-screenshot spectacle grim` |
| Fedora | `sudo dnf install scrot xfce4-screenshooter` | `sudo dnf install gnome-screenshot spectacle grim` |

#### Keyboard Simulation

| Distro | X11 | Wayland |
| :--- | :--- | :--- |
| Debian/Ubuntu | `sudo apt install xdotool` | `sudo apt install ydotool` |
| Arch/Manjaro | `sudo pacman -S xdotool` | `sudo pacman -S ydotool` |
| Fedora | `sudo dnf install xdotool` | `sudo dnf install ydotool` |

#### Network & System Utilities

| Distro | Command |
| :--- | :--- |
| Debian/Ubuntu | `sudo apt install nmap iproute2 net-tools pciutils procps` |
| Arch/Manjaro | `sudo pacman -S nmap iproute2 net-tools pciutils procps-ng` |
| Fedora | `sudo dnf install nmap iproute net-tools pciutils procps-ng` |

#### Browser Utilities

```bash
# All distros
sudo apt install xdg-utils      # Debian/Ubuntu
sudo pacman -S xdg-utils        # Arch/Manjaro
sudo dnf install xdg-utils      # Fedora
```

---

## 🚀 Full Installation (by distro)

### Ubuntu / Debian / Mint

```bash
sudo apt update
sudo apt install -y python3 python3-pip xdotool ydotool scrot gnome-screenshot spectacle grim xfce4-screenshooter nmap xdg-utils iproute2 net-tools procps pciutils
pip3 install pyTelegramBotAPI psutil
```

### Arch / Manjaro

```bash
sudo pacman -Sy
sudo pacman -S --noconfirm python python-pip xdotool ydotool scrot gnome-screenshot spectacle grim xfce4-screenshooter nmap xdg-utils iproute2 net-tools procps-ng pciutils
pip install pyTelegramBotAPI psutil
```

### Fedora / RHEL

```bash
sudo dnf check-update
sudo dnf install -y python3 python3-pip xdotool ydotool scrot gnome-screenshot spectacle grim xfce4-screenshooter nmap xdg-utils iproute net-tools procps-ng pciutils
pip3 install pyTelegramBotAPI psutil
```

### Minimal Installation (shell only)

```bash
# Debian/Ubuntu
sudo apt install python3 python3-pip
pip3 install pyTelegramBotAPI psutil

# Arch/Manjaro
sudo pacman -S python python-pip
pip install pyTelegramBotAPI psutil

# Fedora
sudo dnf install python3 python3-pip
pip3 install pyTelegramBotAPI psutil
```

---

## ⚙️ Installation Guide

### 1. Clone Repository

```bash
git clone https://github.com/venya11/radhaunt_agent.git
cd radhaunt_agent
chmod +x radhaunt_agent.py
```

### 2. Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create `.env` file and configure security:

```env
RADHAUNT_API_TOKEN=your_telegram_bot_token
RADHAUNT_ADMIN_ID=your_telegram_user_id
RADHAUNT_USER_SYSTEM=your_linux_username
RADHAUNT_SUDO_PASSWD=your_sudo_password
```

```bash
chmod 600 .env
```

---

## 🖥️ Persistent Autostart

### Method A: Systemd (Recommended)

**Create service file:**

```bash
sudo nano /etc/systemd/system/radhaunt_agent.service
```

**Paste configuration:**
(change values in {} on your real data):

```ini
[Unit]
Description=RadHaunt Telegram Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User={YOUR_USER}
Group={YOUR_USER}
ExecStart=/home/{YOUR_USER}/{PATH_TO_PROJECT}/venv/bin/python /home/{YOUR_USER}/{PATH_TO_PROJECT}/radhaunt_agent.py
WorkingDirectory=/home/{YOUR_USER}/{PATH_TO_PROJECT}/

EnvironmentFile=/home/{YOUR_USER}/{PATH_TO_PROJECT}/.env

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo chmod 600 /etc/systemd/system/radhaunt_agent.service
sudo systemctl daemon-reload
sudo systemctl enable radhaunt_agent.service
sudo systemctl start radhaunt_agent.service
sudo systemctl status radhaunt_agent.service
sudo journalctl -u radhaunt_agent.service -f
```

### Method B: XDG Autostart

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/radhaunt_agent.desktop
```

```desktop
[Desktop Entry]
Type=Application
Name=RadHaunt Agent
Exec=env RADHAUNT_API_TOKEN="YOUR_TOKEN" RADHAUNT_ADMIN_ID="YOUR_ID" RADHAUNT_USER_SYSTEM="YOUR_USERNAME" RADHAUNT_SUDO_PASSWD="YOUR_PASSWORD" /home/YOUR_USER/PATH_TO_PROJECT/venv/bin/python /home/YOUR_USER/PATH_TO_PROJECT/radhaunt_agent.py
Terminal=false
X-GNOME-Autostart-enabled=true
```

### Method C: Crontab

```bash
crontab -e
@reboot cd /home/YOUR_USER/PATH_TO_PROJECT && ./venv/bin/python radhaunt_agent.py
```

### Method D: OpenRC

```bash
sudo nano /etc/init.d/radhaunt_agent
sudo chmod +x /etc/init.d/radhaunt_agent
sudo rc-update add radhaunt_agent default
sudo rc-service radhaunt_agent start
```

---

## ✅ Verification

Send `/start` to your bot in Telegram.

**Expected response:**

```
🤖 Hello! Agent has been started. Waiting for shell commands, or enter '/help'.
```