import sqlite3
import time
import telebot

TOKEN = "9243015031:AAEM9UV1CPbyNJWCKOxQNoQ5focMQBTnzZI"
bot = telebot.TeleBot(TOKEN)

# Initialize Database
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    uid TEXT
)
"""
)
conn.commit()


@bot.message_handler(commands=["start"])
def start(message):
  bot.reply_to(
      message,
      "Welcome to La Wes FF Like Exchange! 🔥\nJust send your FF UID number"
      " straight (e.g. `15326110918`) or use `/setuid YOUR_UID`",
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["setuid"])
def setuid_command(message):
  try:
    parts = message.text.split()
    if len(parts) > 1:
      uid = parts[1]
    else:
      bot.reply_to(message, "Oga, use space like this: /setuid 15326110918")
      return
    save_uid(message.from_user.id, uid, message)
  except Exception as e:
    bot.reply_to(message, "Use am like this: /setuid 123456789")


# Catch normal text messages that look like a Free Fire UID (numbers only)
@bot.message_handler(
    func=lambda msg: msg.text and msg.text.isdigit() and len(msg.text) > 5
)
def handle_direct_uid(message):
  save_uid(message.from_user.id, message.text.strip(), message)


def save_uid(user_id, uid, message):
  cursor.execute(
      "INSERT OR REPLACE INTO users (user_id, uid) VALUES (?, ?)",
      (user_id, uid),
  )
  conn.commit()
  bot.reply_to(
      message,
      f"Your UID `{uid}` don save! ✅\nNow use /getlikes to get person to like.",
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["getlikes"])
def getlikes(message):
  user_id = message.from_user.id
  cursor.execute("SELECT uid FROM users WHERE user_id != ?", (user_id,))
  others = cursor.fetchall()

  if not others:
    bot.reply_to(
        message, "No person don join yet. Share this bot make people join."
    )
  else:
    target_uid = others[0][0]
    bot.reply_to(
        message,
        f"Go like this UID for Free Fire:\n`{target_uid}`\nAfter you like am,"
        " press /done",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["done"])
def done(message):
  bot.reply_to(
      message,
      "Nice one! ❤️ You don do your own. Your UID go show to next person.",
  )


@bot.message_handler(commands=["myuid"])
def myuid(message):
  user_id = message.from_user.id
  cursor.execute("SELECT uid FROM users WHERE user_id = ?", (user_id,))
  result = cursor.fetchone()

  if result:
    bot.reply_to(message, f"Your UID: {result[0]}")
  else:
    bot.reply_to(
        message, "You never set UID yet. Just send your UID number or /setuid"
    )


print("Clearing webhooks and starting bot...")
try:
  bot.remove_webhook()  # This clears any stuck webhooks on Telegram
except Exception as e:
  print(f"Webhook clear warning: {e}")

print("La Wes Bot dey run smoothly...")

while True:
  try:
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
  except Exception as e:
    print(f"Connection dropped: {e}. Reconnecting...")
    time.sleep(5)
