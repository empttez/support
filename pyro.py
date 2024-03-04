import pyrogram
from pyrogram import Client, filters
import values

# Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота Telegram.
app = Client(
  name="pyrotest",
  api_id=values.id,
  api_hash=values.hash,
  app_version=f"Pyro Test Bot v0.1",
  bot_token=values.token,
  parse_mode=pyrogram.enums.ParseMode.HTML
)


@app.on_message(filters.command("start", prefixes=["!./"]))
def start_command(client, message):
    client.send_message(message.chat.id, "Привет!")

app.run()
