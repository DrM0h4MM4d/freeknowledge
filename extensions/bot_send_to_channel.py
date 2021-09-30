from pyrogram import Client
from decuple import config

app = Client("bot", api_id=config("TELEGRAM_API_ID"), api_hash=config("TELEGRAM_API_HASH"), 
                            bot_token=config('TELEGRAM_BOT_TOKEN'))
chat_id = -1001468937443

app.start()

def send_to_channel(name, image, text, link):
    text = text[0:300]
    app.send_photo(chat_id=chat_id, photo=image, 
caption=f"""
**{name}**

{text}...

لینک در وبسایت: {link}
""")
    return 1

app.stop()
