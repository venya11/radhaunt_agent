import telebot
import subprocess
import os
import html
import platform
import time
import shutil
import psutil

actual_wayland_display = os.getenv("WAYLAND_DISPLAY", "wayland-0")

# --- API, SETTINGS AND SECURITY ---
API_TOKEN = os.getenv("RADHAUNT_API_TOKEN")
ADMIN_ID = int(os.getenv("RADHAUNT_ADMIN_ID", "0"))
ADMIN_USER_SYSTEM = os.getenv("RADHAUNT_USER_SYSTEM")
ADMIN_USER_SUDO_PASSWD = os.getenv("RADHAUNT_SUDO_PASSWD")

CURRENT_TIMEOUT = 15
bot = telebot.TeleBot(API_TOKEN)

# --- SHELL CHOOSING ---
if shutil.which("bash"):
    chosen_shell = "/bin/bash"
elif shutil.which("sh"):
    chosen_shell = "/bin/sh"
elif shutil.which("zsh"):
    chosen_shell = "/bin/zsh"
else:
    chosen_shell = "/bin/sh"

# --- SESSION DETECTION ---
session_type = "unknown"
desktop_env = ""
ps_output = ""
try:
    session_type = subprocess.check_output("echo $XDG_SESSION_TYPE", shell=True, text=True).strip().lower()
    ps_output = subprocess.check_output("ps -e", shell=True, text=True).lower()
    desktop_env = subprocess.check_output("echo $XDG_CURRENT_DESKTOP", shell=True, text=True).strip().lower()
    if not session_type or session_type == "tty":
        if any(wm in ps_output for wm in ["wayland", "hyprland", "sway"]):
            session_type = "wayland"
        elif "xorg" in ps_output or "x" in ps_output:
            session_type = "x11"        
    if session_type == "x11":
        os.environ["DISPLAY"] = ":0"
        os.environ["XAUTHORITY"] = f"/home/{ADMIN_USER_SYSTEM}/.Xauthority"
except Exception:
    pass

# --- SCREENSHOT ---
def take_fast_screenshot(photo_path):
    if session_type == "wayland":
        if "gnome" in desktop_env:
            cmd = f"gdbus call --session --dest org.gnome.Shell.Screenshot --object-path /org/gnome/Shell/Screenshot --method org.gnome.Shell.Screenshot.Screenshot false true '{photo_path}'"
            subprocess.run(cmd, shell=True, timeout=5)
        else:
            subprocess.run(f"grim {photo_path}", shell=True, timeout=5)
    else:
        try:
            from mss import mss
            with mss() as sct:
                sct.shot(output=photo_path)
        except Exception:
            if not os.environ.get("XAUTHORITY"):
                for path in [f"/home/{ADMIN_USER_SYSTEM}/.Xauthority", f"/run/user/1000/gdm/Xauthority"]:
                    if os.path.exists(path):
                        os.environ["XAUTHORITY"] = path
                        break
            subprocess.run(f"scrot {photo_path} || xfce4-screenshooter -s {photo_path}", shell=True, timeout=5)

# --- NETWORK FUNCTIONS ---
def get_network_info():
    info = {}
    try:
        net_io = psutil.net_io_counters()
        info['bytes_sent'] = net_io.bytes_sent
        info['bytes_recv'] = net_io.bytes_recv
        info['packets_sent'] = net_io.packets_sent
        info['packets_recv'] = net_io.packets_recv
        info['errin'] = net_io.errin
        info['errout'] = net_io.errout
        info['dropin'] = net_io.dropin
        info['dropout'] = net_io.dropout
    except:
        pass
    try:
        if shutil.which("ss"):
            result = subprocess.run(["ss", "-tunap"], capture_output=True, text=True, timeout=5)
            connections = result.stdout.split('\n')[1:]
            info['connections'] = [conn for conn in connections if conn.strip()]
        elif shutil.which("netstat"):
            result = subprocess.run(["netstat", "-tunap"], capture_output=True, text=True, timeout=5)
            connections = result.stdout.split('\n')[2:]
            info['connections'] = [conn for conn in connections if conn.strip()]
        else:
            info['connections'] = ["ss or netstat is not installed"]
    except:
        info['connections'] = ["Error retrieving connections"]
    
    try:
        if shutil.which("ss"):
            result = subprocess.run(["ss", "-tuln"], capture_output=True, text=True, timeout=5)
            listening = result.stdout.split('\n')[1:]
            info['listening_ports'] = [port for port in listening if port.strip() and 'LISTEN' in port]
        elif shutil.which("netstat"):
            result = subprocess.run(["netstat", "-tuln"], capture_output=True, text=True, timeout=5)
            listening = result.stdout.split('\n')[2:]
            info['listening_ports'] = [port for port in listening if port.strip() and 'LISTEN' in port]
        else:
            info['listening_ports'] = ["ss or netstat is not installed"]
    except:
        info['listening_ports'] = ["Error retrieving ports"]
    try:
        result = subprocess.run(["ip", "addr"], capture_output=True, text=True, timeout=3)
        interfaces = []
        current_iface = {}
        for line in result.stdout.split('\n'):
            if ':' in line and not line.strip().startswith(' '):
                if current_iface:
                    interfaces.append(current_iface)
                iface_name = line.split(':')[1].strip()
                current_iface = {'name': iface_name, 'ips': []}
            elif 'inet ' in line or 'inet6 ' in line:
                ip = line.strip().split()[1]
                current_iface['ips'].append(ip)
        if current_iface:
            interfaces.append(current_iface)
        info['interfaces'] = interfaces
    except:
        info['interfaces'] = ["Error retrieving interfaces"]
    try:
        with open('/etc/resolv.conf', 'r') as f:
            dns = [line.split()[1] for line in f if line.startswith('nameserver')]
        info['dns_servers'] = dns
    except:
        info['dns_servers'] = ["Error retrieving DNS"]
    suspicious = []
    if 'connections' in info:
        for conn in info['connections']:
            conn_lower = conn.lower()
            suspicious_ports = ['23', '25', '445', '1433', '3306', '3389', '5900', '6667', '6697']
            if any(f':{port}' in conn or f':{port} ' in conn for port in suspicious_ports):
                suspicious.append(conn)
            if 'ESTAB' in conn or 'SYN' in conn:
                parts = conn.split()
                if len(parts) >= 6:
                    local = parts[4]
                    remote = parts[5]
                    if remote and not remote.startswith('127.') and not remote.startswith('10.') and not remote.startswith('192.168.') and not remote.startswith('172.'):
                        if ':' in remote and '[' not in remote:  # IPv4
                            suspicious.append(f"⚠️ Outgoing connection: {conn}")
    info['suspicious'] = suspicious[:10]
    return info
def format_network_info(info):
    def bytes_to_human(b):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if b < 1024.0:
                return f"{b:.2f} {unit}"
            b /= 1024.0
        return f"{b:.2f} PB"
    
    lines = [
        "🌐 <b>NETWORK STATUS</b>\n",
        "═══════════════════════════",
    ]
    if 'bytes_sent' in info:
        lines.append("\n📊 <b>Traffic Statistics:</b>")
        lines.append(f"📤 Sent: {bytes_to_human(info['bytes_sent'])}")
        lines.append(f"📥 Received: {bytes_to_human(info['bytes_recv'])}")
        lines.append(f"📦 Packets sent: {info.get('packets_sent', 0):,}")
        lines.append(f"📦 Packets recv: {info.get('packets_recv', 0):,}")
        lines.append(f"❌ Errors in: {info.get('errin', 0)}")
        lines.append(f"❌ Errors out: {info.get('errout', 0)}")
        lines.append(f"💧 Dropped in: {info.get('dropin', 0)}")
        lines.append(f"💧 Dropped out: {info.get('dropout', 0)}")
    
    if 'interfaces' in info and isinstance(info['interfaces'], list):
        lines.append("\n🖧 <b>Network Interfaces:</b>")
        for iface in info['interfaces']:
            if isinstance(iface, dict) and 'name' in iface:
                ips = ', '.join(iface.get('ips', ['no IP']))
                lines.append(f"  • {iface['name']}: {ips}")
    
    if 'dns_servers' in info:
        lines.append("\n🌍 <b>DNS Servers:</b>")
        for dns in info['dns_servers']:
            lines.append(f"  • {dns}")
    
    if 'listening_ports' in info:
        lines.append("\n🔓 <b>Listening Ports (Open):</b>")
        ports = info['listening_ports']
        if ports and len(ports) > 0:
            for port in ports[:15]:
                lines.append(f"  • {port}")
            if len(ports) > 15:
                lines.append(f"  ... and {len(ports) - 15} more")
        else:
            lines.append("  No listening ports found")
    
    if 'suspicious' in info and info['suspicious']:
        lines.append("\n⚠️ <b>SUSPICIOUS CONNECTIONS:</b>")
        for susp in info['suspicious']:
            lines.append(f"  • {susp}")

    if 'connections' in info:
        conn_count = len(info['connections'])
        est_count = sum(1 for c in info['connections'] if 'ESTAB' in c)
        lines.append(f"\n🔗 <b>Active Connections:</b> {conn_count} total, {est_count} established")
        if conn_count > 0:
            lines.append("  <i>Showing first 10 connections:</i>")
            for conn in info['connections'][:10]:
                if len(conn) > 80:
                    conn = conn[:77] + "..."
                lines.append(f"  • {conn}")
            if conn_count > 10:
                lines.append(f"  ... and {conn_count - 10} more")
    
    return "\n".join(lines)

# --- START ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "🤖 Hello! Agent has been started. Waiting for shell commands, or enter '/help'.")
    else:
        bot.reply_to(message, "Access denied.")

# -- HELP ---
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "<b>RadHaunt Agent v1.3</b>\n\n"
        "Type and send any shell command to your linux system (ex. whoami, ls)\n\n"
        "<b>Important!!!</b> When running graphical programs, use '&' after the command (ex. firefox &)\n\n"
        "<b>Agent also has his own commands:</b>\n\n"
        "- Net (Shows network statistics, connections, open ports, and suspicious connections)\n\n"
            "   Additional arguments: Net scan (or net scan {subnet_mask}) - scans the local network for active hosts\n"
            "       Net scan ports (or net scan ports {subnet_mask}) - scans for active hosts and open ports\n"
        "- Download {path_to_file} (downloading and sends file to the chat)\n\n"
        "- Upload (uploading file on server) P.S just send any file as document in this chat\n\n"
        "- Screenshot (Takes a screenshot and sends it to the chat)\n\n"
        "- Show info (Displays basic system information)\n\n"
        "- Keyboard (Provides access to the main keys with buttons)\n\n"
        "- Type {text} (Enters specific text like a human)\n\n"
        "- Url {link} (Opens any link dynamically in your system browser. IMPORTANT: The browser should not be open before this or it will crash. )\n\n"
        "- Timeout {value} (Setting max timeout(in seconds) limit for shell commands. Default 15.)"
    )
    bot.reply_to(message, help_text, parse_mode='HTML')

# --- UPLOAD HANDLER ---
@bot.message_handler(content_types=['document'])
def handle_upload_document(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        file_name = message.document.file_name
        file_info = bot.get_file(message.document.file_id)
        destination_path = os.path.join(os.getcwd(), file_name)
        status_msg = bot.send_message(ADMIN_ID, f"📥 <b>Uploading file</b> <code>{html.escape(file_name)}</code> on server...", parse_mode='HTML')
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(destination_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.edit_message_text(
            chat_id=ADMIN_ID,
            message_id=status_msg.message_id,
            text=f"✅ <b>File successfully uploaded!!</b>\n📍 Path: <code>{html.escape(destination_path)}</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ <b>Error:</b> {str(e)}", parse_mode='HTML')

# --- MAIN ---    
@bot.message_handler(func=lambda message: True)
def execute_command(message):
    global CURRENT_TIMEOUT

    if message.from_user.id != ADMIN_ID:
        return
    
    global CURRENT_TIMEOUT
    command = message.text.strip()

    try:
        # --- COMMAND: TIMEOUT ---
        if command.lower().startswith('timeout '):
            try:
                new_timeout = int(command[8:].strip())
                if new_timeout <=0:
                    bot.send_message(ADMIN_ID, "⚠️ <b>Timeout must be a positive number!</b>", parse_mode='HTML')
                    return
                CURRENT_TIMEOUT = new_timeout
                bot.send_message(ADMIN_ID, f"⏱️ <b>Timeout updated!</b> New limit: <code>{CURRENT_TIMEOUT}</code> seconds.", parse_mode='HTML')
                return
            except ValueError:
                bot.send_message(ADMIN_ID, "⚠️ <b>Please enter a valid number!</b> (ex. <code>timeout 60</code>)", parse_mode='HTML')
                return

        # --- COMMAND: DOWNLOAD ---
        if command.lower().startswith('download '):
            file_path = command[9:].strip()
            if not file_path:
                bot.send_message(ADMIN_ID, "⚠️ <b>Enter a path to file!</b> (exmpl, <code>download /etc/hosts</code>)", parse_mode='HTML')
                return
            file_path = os.path.expanduser(file_path)
            if not os.path.exists(file_path):
                bot.send_message(ADMIN_ID, f"❌ <b>File not found:</b> <code>{html.escape(file_path)}</code>", parse_mode='HTML')
                return
            if os.path.isdir(file_path):
                bot.send_message(ADMIN_ID, "⚠️ <b>This is directory, not a file!</b>.", parse_mode='HTML')
                return
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                bot.send_message(ADMIN_ID, f"⚠️ <b>The file is too large. ({file_size / (1024*1024):.1f} MB)!</b> Telegram bots limit — 50 MB.", parse_mode='HTML')
                return
            try:
                status_msg = bot.send_message(ADMIN_ID, f"📤 <b>Sending file:</b> <code>{html.escape(os.path.basename(file_path))}</code>...", parse_mode='HTML')
                with open(file_path, 'rb') as doc:
                    bot.send_document(ADMIN_ID, doc, caption=f"📄 File: <code>{html.escape(file_path)}</code>", parse_mode='HTML')
                bot.delete_message(ADMIN_ID, status_msg.message_id)
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"❌ <b>Error:</b> {str(e)}", parse_mode='HTML')
                return
        
        # --- COMMAND: NET ---
        if command.lower() == "net":
            try:
                status_msg = bot.send_message(ADMIN_ID, "🔍 <b>Collecting network data...</b>", parse_mode='HTML')
                net_info = get_network_info()
                formatted_info = format_network_info(net_info)
                bot.edit_message_text(
                    chat_id=ADMIN_ID,
                    message_id=status_msg.message_id,
                    text=formatted_info,
                    parse_mode='HTML'
                )
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"⚠️ <b>Error collecting network info:</b> {str(e)}", parse_mode='HTML')
                return

        # --- COMMAND: NET SCAN PORTS ---
        if command.lower().startswith("net scan ports"):
            try:
                status_msg = bot.send_message(ADMIN_ID, "🔍 <b>Scanning network ports and versions...</b>", parse_mode='HTML')
                parts = command.split()
                if len(parts) > 3:
                    subnet = parts[3]
                else:
                    try:
                        raw_ip = subprocess.check_output("hostname -I | awk '{print $1}'", shell=True, text=True).strip()
                        if raw_ip and "." in raw_ip:
                            subnet = ".".join(raw_ip.split(".")[:3]) + ".0/24"
                        else:
                            subnet = "192.168.1.0/24"
                    except Exception:
                        subnet = "192.168.1.0/24"
                cmd_args = ["nmap", "-F", "-sV", subnet]
                result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=180)
                if result.stdout:
                    output = f"📡 <b>Network Scan Results (Ports):</b>\n\n<pre><code>{html.escape(result.stdout[:3500])}</code></pre>"
                else:
                    output = f"⚠️ No results or error:\n<code>{html.escape(result.stderr)}</code>"
                
                bot.edit_message_text(chat_id=ADMIN_ID, message_id=status_msg.message_id, text=output, parse_mode='HTML')
                return
            except subprocess.TimeoutExpired:
                bot.edit_message_text(chat_id=ADMIN_ID, message_id=status_msg.message_id, text="⏰ <b>Scan timed out!</b> Network is too slow or large.", parse_mode='HTML')
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"⚠️ <b>Network scan error:</b> {str(e)}", parse_mode='HTML')
                return

        # --- COMMAND: NET SCAN ---
        if command.lower().startswith("net scan") and not command.lower().startswith("net scan ports"):
            try:
                status_msg = bot.send_message(ADMIN_ID, "🔍 <b>Scanning network hosts (Ping Scan)...</b>", parse_mode='HTML')
                parts = command.split()
                if len(parts) > 2:
                    subnet = parts[2]
                else:
                    try:
                        raw_ip = subprocess.check_output("hostname -I | awk '{print $1}'", shell=True, text=True).strip()
                        subnet = ".".join(raw_ip.split(".")[:3]) + ".0/24" if raw_ip else "192.168.1.0/24"
                    except Exception:
                        subnet = "192.168.1.0/24"
                cmd_args = ["nmap", "-sn", subnet]
                result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=45)
                if result.stdout:
                    output = f"📡 <b>Network Scan Results (Hosts):</b>\n\n<pre><code>{html.escape(result.stdout[:3500])}</code></pre>"
                else:
                    output = "⚠️ No hosts found."
                bot.edit_message_text(chat_id=ADMIN_ID, message_id=status_msg.message_id, text=output, parse_mode='HTML')
                return
            except subprocess.TimeoutExpired:
                bot.edit_message_text(chat_id=ADMIN_ID, message_id=status_msg.message_id, text="⏰ <b>Scan timed out!</b>", parse_mode='HTML')
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"⚠️ <b>Network scan error:</b> {str(e)}", parse_mode='HTML')
                return
            
        # --- COMMAND: SCREENSHOT ---
        if command.lower() == "screenshot":
            photo_path = "/tmp/screenshot.png"
            try:
                take_fast_screenshot(photo_path)
                if os.path.exists(photo_path):
                    env_info = desktop_env.upper() if desktop_env else "CUSTOM/TILING"
                    with open(photo_path, "rb") as photo:
                        bot.send_photo(ADMIN_ID, photo, caption=f"Screenshot completed.\n🖥️ DE: {env_info}\n⚙️ GraphServer: {session_type.upper()}")
                    os.remove(photo_path)
                else:
                    raise Exception("Screenshot file not found.")
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"Error: {str(e)}")
                return
        
        # --- COMMAND: SHOW INFO ---
        if command.lower() == "show info":
            try:
                os_type = platform.system()        
                kernel = platform.release()        
                arch = platform.machine()           
                hostname = platform.node()          
                internal_ip = subprocess.check_output("hostname -I | awk '{print $1}'", shell=True, text=True).strip() or "Unknown"
                ram_info = subprocess.check_output("free -h | grep Mem | awk '{print $3 \" / \" $2}'", shell=True, text=True).strip() or "Unknown"
                cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -n 1 | awk -F: '{print $2}'", shell=True, text=True).strip() or "Unknown"
                gpu_info = subprocess.check_output('lspci | grep -E "VGA|3D" | awk -F: \'{print $3}\'', shell=True, text=True).strip() or "Unknown"

                info_message = (
                    f"📋 <b>SYSTEM INFO REPORT</b>\n\n"
                    f"🖥️ <b>Host:</b> {hostname}\n"
                    f"🐧 <b>OS:</b> {os_type} {arch}\n"
                    f"⚙️ <b>Kernel:</b> {kernel}\n"
                    f"🧠 <b>CPU:</b> {cpu_info}\n"
                    f"🎮 <b>GPU:</b> {gpu_info}\n"
                    f"💾 <b>RAM (Used/Total):</b> {ram_info}\n"
                    f"🌐 <b>Local IP:</b> <code>{internal_ip}</code>"
                )
                bot.send_message(ADMIN_ID, info_message, parse_mode='HTML')
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"Error in show info: {str(e)}")
                return
            
        # --- COMMAND: KEYBOARD ---
        if command.lower() == "keyboard":
            from telebot import types    
            markup       = types.InlineKeyboardMarkup(row_width=4)
            btn_tab      = types.InlineKeyboardButton("⇥ TAB", callback_data="key_Tab_tab")
            btn_up       = types.InlineKeyboardButton("🔼 UP", callback_data="key_Up_up")
            btn_enter    = types.InlineKeyboardButton("↩️ ENTER", callback_data="key_Return_enter")
            btn_back     = types.InlineKeyboardButton("⌫ BACK", callback_data="key_BackSpace_backspace")
            btn_left     = types.InlineKeyboardButton("◀️ LEFT", callback_data="key_Left_left")
            btn_space    = types.InlineKeyboardButton("␣ SPACE", callback_data="key_space_space")
            btn_right    = types.InlineKeyboardButton("▶️ RIGHT", callback_data="key_Right_right")
            btn_esc      = types.InlineKeyboardButton("❌ ESC", callback_data="key_Escape_esc")
            btn_f5       = types.InlineKeyboardButton("🔄 F5", callback_data="key_F5_f5")
            btn_down     = types.InlineKeyboardButton("🔽 DOWN", callback_data="key_Down_down")
            btn_f11      = types.InlineKeyboardButton("📺 F11", callback_data="key_F11_f11")
            btn_win      = types.InlineKeyboardButton("⊞ WIN", callback_data="key_Super_L_super")
            btn_vol_up   = types.InlineKeyboardButton("🔊 VOL +", callback_data="key_XF86AudioRaiseVolume_audioraisevolume")
            btn_vol_down = types.InlineKeyboardButton("🔉 VOL -", callback_data="key_XF86AudioLowerVolume_audiolowervolume")
            btn_mute     = types.InlineKeyboardButton("🔇 MUTE", callback_data="key_XF86AudioMute_audiomute")
            btn_next     = types.InlineKeyboardButton("⏭️ NEXT", callback_data="key_XF86AudioNext_audionext")
            btn_alt_tab  = types.InlineKeyboardButton("🔄 Alt+Tab", callback_data="key_alt+Tab_alt+tab")
            btn_show_d   = types.InlineKeyboardButton("📉 Hide all", callback_data="key_super+d_super+d")
            btn_close    = types.InlineKeyboardButton("💀 Close window", callback_data="key_alt+F4_alt+f4")
            markup.add(btn_tab, btn_up, btn_enter, btn_back)
            markup.add(btn_left, btn_space, btn_right, btn_esc)
            markup.add(btn_down, btn_f5, btn_f11, btn_win)
            markup.add(btn_vol_up, btn_vol_down, btn_mute, btn_next)
            markup.add(btn_alt_tab, btn_show_d)
            markup.add(btn_close)   

            photo_path = "/tmp/keyboard_start.png"
            take_fast_screenshot(photo_path)
            
            if os.path.exists(photo_path):
                with open(photo_path, "rb") as photo:
                    bot.send_photo(ADMIN_ID, photo, caption="<b>Keyboard Mode Active</b>\nControl your layout below:", parse_mode='HTML', reply_markup=markup)
                os.remove(photo_path)
            else:
                bot.send_message(ADMIN_ID, "🎮 <b>Remote button keyboard</b>\n(Screenshot failed, loading keys only):", reply_markup=markup)
            return
        
        # --- COMMAND: TYPE TEXT ---
        if command.lower().startswith('type '):
            text_to_type = command[5:].strip()
            if not text_to_type:
                bot.send_message(ADMIN_ID, "⚠️ <b>Text is empty!</b>", parse_mode='HTML')
                return
            try:
                if session_type == "wayland":
                    p = subprocess.Popen(["sudo", "-S", "ydotool", "type", text_to_type], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    p.communicate(input=f"{ADMIN_USER_SUDO_PASSWD}\n")
                    p2 = subprocess.Popen(["sudo", "-S", "ydotool", "key", "enter"], stdin=subprocess.PIPE, text=True)
                    p2.communicate(input=f"{ADMIN_USER_SUDO_PASSWD}\n")
                else:
                    os.environ["DISPLAY"] = ":0"
                    os.environ["XAUTHORITY"] = f"/home/{ADMIN_USER_SYSTEM}/.Xauthority"
                    subprocess.run(f"xdotool type '{text_to_type}'", shell=True, timeout=5)
                    subprocess.run("xdotool key Return", shell=True, timeout=2)
                bot.send_message(ADMIN_ID, f"<b>Text printed and sent:</b>\n<code>{html.escape(text_to_type)}</code>", parse_mode='HTML')
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"Error: {str(e)}")
                return
            
        # --- COMMAND: URL ---
        if command.lower().startswith('url '):
            target_url = command[4:].strip()
            if not target_url:
                bot.send_message(ADMIN_ID, "⚠️ <b>URL is empty!</b>", parse_mode='HTML')
                return
            if not target_url.startswith(('http://', 'https://')):
                target_url = 'https://' + target_url            
            try:
                bot.send_message(ADMIN_ID, f"🌐 Opening in browser: <code>{html.escape(target_url)}</code>...", parse_mode='HTML')
                custom_env = os.environ.copy()
                if session_type == "wayland":
                    if "WAYLAND_DISPLAY" not in custom_env:
                        custom_env["WAYLAND_DISPLAY"] = os.getenv("WAYLAND_DISPLAY", actual_wayland_display)
                    custom_env["QT_QPA_PLATFORM"] = "wayland"
                    custom_env["MOZ_ENABLE_WAYLAND"] = "1"
                    subprocess.Popen(f"xdg-open '{target_url}'", shell=True, env=custom_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    custom_env["DISPLAY"] = ":0"
                    custom_env["XAUTHORITY"] = f"/home/{ADMIN_USER_SYSTEM}/.Xauthority"
                    subprocess.Popen(f"xdg-open '{target_url}'", shell=True, env=custom_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                bot.send_message(ADMIN_ID, "🚀 <b>Browser launched successfully!</b>", parse_mode='HTML')
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"Error: {str(e)}")
                return

        # --- CD COMMAND ---
        if command.startswith('cd '):
            target_dir = command[3:].strip()
            try:
                os.chdir(target_dir)
                current_dir = os.getcwd()
                bot.send_message(ADMIN_ID, f"Directory changed:\n<code>{current_dir}</code>", parse_mode='HTML')
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"Error: {str(e)}")
                return

        # --- BASE SHELL EXECUTION ---
        if command.startswith('sudo '):
            clean_command = command[5:]
            proc = subprocess.Popen(["sudo", "-S"] + chosen_shell.split() + ["-c", clean_command], 
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd())
            stdout, stderr = proc.communicate(input=f"{ADMIN_USER_SUDO_PASSWD}\n", timeout=CURRENT_TIMEOUT)
        else:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd(), executable=chosen_shell)
            stdout, stderr = proc.communicate(timeout=CURRENT_TIMEOUT)

        output = html.escape(stdout) if stdout else ""
        error = html.escape(stderr) if stderr else ""

        if "[sudo] password for" in error:
            error = ""

        response = ""
        if output:
            response += f"<b>Output:</b>\n<pre><code>{output}</code></pre>\n"
        if error:
            response += f"<b>Error:</b>\n<pre><code>{error}</code></pre>"
        if not response:
            response = "Command executed, output is empty."

        if len(response) > 4000:
            response = response[:4000] + "</code></pre>\n...[Text is shortened]"

        bot.send_message(ADMIN_ID, response, parse_mode='HTML')

    except subprocess.TimeoutExpired:
        bot.send_message(ADMIN_ID, f"⚠️ <b>The command timed out (current limit: {CURRENT_TIMEOUT} sec).</b>", parse_mode='HTML')
    except Exception as e:
        bot.send_message(ADMIN_ID, f"System error: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('key_'))
def handle_keyboard_click(call):
    if call.from_user.id != ADMIN_ID:
        return
    data_parts = call.data.split('_')
    x11_key = data_parts[1]
    wayland_key = data_parts[2] if len(data_parts) > 2 else x11_key.lower()
    try:
        if session_type == "wayland":
            p = subprocess.Popen(["sudo", "-S", "ydotool", "key", wayland_key], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p.communicate(input=f"{ADMIN_USER_SUDO_PASSWD}\n", timeout=3)
        else:
            subprocess.run(f"xdotool key {x11_key}", shell=True, timeout=2)
        time.sleep(0.3)    
        bot.answer_callback_query(call.id, text=f"Pressed: {x11_key}")
        photo_path = "/tmp/keyboard_refresh.png"
        take_fast_screenshot(photo_path)
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                bot.edit_message_media(
                    media=telebot.types.InputMediaPhoto(photo, caption="🎮 <b>Keyboard Mode Active</b>\nScreen updated automatically:"),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=call.message.reply_markup
                )
            os.remove(photo_path)
    except Exception as e:
        bot.answer_callback_query(call.id, text=f"Error: {str(e)}")


if __name__ == '__main__':
    try:
        bot.send_message(ADMIN_ID, "<b>🐧 System and agent have started!</b> Ready for operations.", parse_mode='HTML')
    except Exception as e:
        print(f"Error sending start message: {e}")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception:
            time.sleep(5)