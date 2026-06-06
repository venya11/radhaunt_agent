import telebot
import subprocess
import os
import html

API_TOKEN = ''
ADMIN_ID = 
ADMIN_USER_SYSTEM = ''
ADMIN_USER_SUDO_PASSWD = ''

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "🤖 Hello, boss! System has been started. Waiting for commands.")
    else:
        bot.reply_to(message, "Access denied.")

@bot.message_handler(func=lambda message: True)
def execute_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    command = message.text.strip()

    try:


        if command.lower() == "screenshot":
            photo_path = "/tmp/screenshot.png"
            try:
                session_type = subprocess.check_output("echo $XDG_SESSION_TYPE", shell=True, text=True).strip().lower()
                desktop_env = subprocess.check_output("echo $XDG_CURRENT_DESKTOP", shell=True, text=True).strip().lower()
                ps_output = subprocess.check_output("ps -e", shell=True, text=True).lower()
                if not session_type or session_type == "tty":
                    if "wayland" in ps_output or "hyprland" in ps_output or "sway" in ps_output:
                        session_type = "wayland"
                    elif "xorg" in ps_output or "x" in ps_output:
                        session_type = "x11"

                if session_type == "wayland":
                    if "gnome" in desktop_env:
                        subprocess.run(f"gnome-screenshot -f {photo_path}", shell=True, timeout=5)
                    elif "kde" in desktop_env:
                        subprocess.run(f"spectacle -b -n -o {photo_path}", shell=True, timeout=5)
                    elif "hyprland" in ps_output or "sway" in ps_output:
                        subprocess.run(f"grim {photo_path}", shell=True, timeout=5)
                    else:
                        subprocess.run(f"grim {photo_path} || spectacle -b -n -o {photo_path}", shell=True, timeout=5)
                else:
                    os.environ["DISPLAY"] = ":0"
                    os.environ["XAUTHORITY"] = f"/home/{ADMIN_USER_SYSTEM}/.Xauthority"
                    try:
                        from mss import mss
                        with mss() as sct:
                            sct.shot(output=photo_path)
                    except Exception:
                        subprocess.run(f"scrot {photo_path} || xfce4-screenshooter -s {photo_path}", shell=True, timeout=5)

                if os.path.exists(photo_path):
                    env_info = desktop_env.upper() if desktop_env else "CUSTOM/TILING"
                    with open(photo_path, "rb") as photo:
                        bot.send_photo(ADMIN_ID, photo, caption=f"Screenshot completed.\n🖥️ DE: {env_info}\n⚙️ GraphServer: {session_type.upper()}")
                    os.remove(photo_path)
                else:
                    raise Exception("Not allowed on your system(DE,Session Type)")
                return

            except Exception as e:
                bot.send_message(ADMIN_ID, f"Error: {str(e)}")
                return
            

        if command.startswith('cd '):
            target_dir = command[3:].strip()
            try:
                os.chdir(target_dir)
                current_dir = os.getcwd()
                bot.send_message(ADMIN_ID, f"Directory changed:\n<code>{current_dir}</code>", parse_mode='HTML')
                return
            except Exception as e:
                bot.send_message(ADMIN_ID, f"Error: {str(e)}")
            

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
    
if __name__ == '__main__':
    bot.infinity_polling()