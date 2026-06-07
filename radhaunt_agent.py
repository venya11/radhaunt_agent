import telebot
import subprocess
import os
import html
import platform

API_TOKEN = ''
ADMIN_ID = 
ADMIN_USER_SYSTEM = ''
ADMIN_USER_SUDO_PASSWD = ''

bot = telebot.TeleBot(API_TOKEN)

def take_fast_screenshot(session_type, desktop_env, ps_output, photo_path):
    if session_type == "wayland":
        if "gnome" in desktop_env:
            subprocess.run(f"gnome-screenshot -f {photo_path}", shell=True, timeout=3)
        elif "kde" in desktop_env:
            subprocess.run(f"spectacle -b -n -o {photo_path}", shell=True, timeout=3)
        else:
            subprocess.run(f"grim {photo_path}", shell=True, timeout=3)
    else:
        try:
            from mss import mss
            with mss() as sct:
                sct.shot(output=photo_path)
        except Exception:
            subprocess.run(f"scrot {photo_path} || xfce4-screenshooter -s {photo_path}", shell=True, timeout=3)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "🤖 Hello! Agent has been started. Waiting for shell commands, or enter '/help'.")
    else:
        bot.reply_to(message, "Access denied.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "<b>RadHaunt Agent v1.1</b>\n\n"
        "Type and send any shell command to your linux system (ex. whoami, ls)\n\n"
        "<b>Important!!!</b> When running graphical programs, use '&' after the command (ex. firefox &)\n\n"
        "<b>Agent also has his own commands:</b>\n\n"
        "- Screenshot (Making screenshot and sending it in this chat)\n\n"
        "- Show info (Outputs basics info about system)\n\n"
        "- Keyboard (Provides access to the main keys with buttons)\n\n"
        "- Type {text} (Enters specific text like a human)\n"
    )
    bot.reply_to(message, help_text, parse_mode='HTML')
    
@bot.message_handler(func=lambda message: True)
def execute_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    command = message.text.strip()

    try:
        try:
            session_type = subprocess.check_output("echo $XDG_SESSION_TYPE", shell=True, text=True).strip().lower()
            ps_output = subprocess.check_output("ps -e", shell=True, text=True).lower()
            if not session_type or session_type == "tty":
                if "wayland" in ps_output or "hyprland" in ps_output or "sway" in ps_output:
                    session_type = "wayland"
                elif "xorg" in ps_output or "x" in ps_output:
                    session_type = "x11"
            if session_type == "x11":
                os.environ["DISPLAY"] = ":0"
                os.environ["XAUTHORITY"] = f"/home/{ADMIN_USER_SYSTEM}/.Xauthority"
        except Exception:
            session_type = "unknown"
            ps_output = ""

        # --- COMMAND: SCREENSHOT ---
        if command.lower() == "screenshot":
            photo_path = "/tmp/screenshot.png"
            try:
                desktop_env = subprocess.check_output("echo $XDG_CURRENT_DESKTOP", shell=True, text=True).strip().lower()
                take_fast_screenshot(session_type, desktop_env, ps_output, photo_path)

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
                cpu_info = subprocess.check_output("cat /proc/proc/cpuinfo | grep 'model name' | head -n 1 | awk -F: '{print $2}'", shell=True, text=True).strip() or "Unknown"
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
            markup = types.InlineKeyboardMarkup(row_width=4)
            btn_tab   = types.InlineKeyboardButton("⇥ TAB", callback_data="key_Tab_tab")
            btn_up    = types.InlineKeyboardButton("🔼 UP", callback_data="key_Up_up")
            btn_enter = types.InlineKeyboardButton("↩️ ENTER", callback_data="key_Return_enter")
            btn_back  = types.InlineKeyboardButton("⌫ BACK", callback_data="key_BackSpace_backspace")
            btn_left  = types.InlineKeyboardButton("◀️ LEFT", callback_data="key_Left_left")
            btn_space = types.InlineKeyboardButton("␣ SPACE", callback_data="key_space_space")
            btn_right = types.InlineKeyboardButton("▶️ RIGHT", callback_data="key_Right_right")
            btn_esc   = types.InlineKeyboardButton("❌ ESC", callback_data="key_Escape_esc")
            btn_f5    = types.InlineKeyboardButton("🔄 F5", callback_data="key_F5_f5")
            btn_down  = types.InlineKeyboardButton("🔽 DOWN", callback_data="key_Down_down")
            btn_f11   = types.InlineKeyboardButton("📺 F11", callback_data="key_F11_f11")
            btn_win   = types.InlineKeyboardButton("⊞ WIN", callback_data="key_Super_L_super")
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
            desktop_env = subprocess.check_output("echo $XDG_CURRENT_DESKTOP", shell=True, text=True).strip().lower()
            take_fast_screenshot(session_type, desktop_env, ps_output, photo_path)
            
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
                    subprocess.run(f"echo '{ADMIN_USER_SUDO_PASSWD}' | sudo -S ydotool type '{text_to_type}'", shell=True, timeout=5)
                    subprocess.run(f"echo '{ADMIN_USER_SUDO_PASSWD}' | sudo -S ydotool key enter", shell=True, timeout=2)
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
        if command.startswith('sudo'):
            clean_command = command[5:]
            full_command = f"echo '{ADMIN_USER_SUDO_PASSWD}' | sudo -S {clean_command}"
        else:
            full_command = command
            
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=15, cwd=os.getcwd())
        
        output = html.escape(result.stdout) if result.stdout else ""
        error = html.escape(result.stderr) if result.stderr else ""

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
        bot.send_message(ADMIN_ID, "The command timed out (timeout 15 sec).")
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
        session_type = subprocess.check_output("echo $XDG_SESSION_TYPE", shell=True, text=True).strip().lower()
        ps_output = subprocess.check_output("ps -e", shell=True, text=True).lower()
        if not session_type or session_type == "tty":
            if "wayland" in ps_output or "hyprland" in ps_output or "sway" in ps_output:
                session_type = "wayland"
            elif "xorg" in ps_output or "x" in ps_output:
                session_type = "x11"
                
        if session_type == "wayland":
            subprocess.run(f"echo '{ADMIN_USER_SUDO_PASSWD}' | sudo -S ydotool key {wayland_key}", shell=True, timeout=2)
        else:
            os.environ["DISPLAY"] = ":0"
            os.environ["XAUTHORITY"] = f"/home/{ADMIN_USER_SYSTEM}/.Xauthority"
            subprocess.run(f"xdotool key {x11_key}", shell=True, timeout=2)
            
        bot.answer_callback_query(call.id, text=f"Pressed: {x11_key}")
        
        photo_path = "/tmp/keyboard_refresh.png"
        desktop_env = subprocess.check_output("echo $XDG_CURRENT_DESKTOP", shell=True, text=True).strip().lower()
        take_fast_screenshot(session_type, desktop_env, ps_output, photo_path)

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
        print(f"Error: {e}")
    bot.infinity_polling()