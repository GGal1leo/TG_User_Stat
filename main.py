from telethon.sync import TelegramClient, events
import os


# get variables from .env file
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")


with TelegramClient("name", api_id, api_hash) as client:
    client.send_message("me", "Hello, myself!")
    print(client.download_profile_photo("me"))

    @client.on(events.NewMessage(pattern="(?i).*Hello"))
    async def handler(event):
        await event.reply("Hey!")

    client.run_until_disconnected()
