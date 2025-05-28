#!/usr/bin/env python3

import os
import re
import telethon
from time import sleep
from telethon import events
from dotenv import load_dotenv
import requests
from database import IOCDatabase

load_dotenv()

assert os.getenv("API_ID") is not None, "API_ID is not set in .env file"
assert os.getenv("API_HASH") is not None, "API_HASH is not set in .env file"

API_ID = str(os.getenv("API_ID"))
API_HASH = str(os.getenv("API_HASH"))

client = telethon.TelegramClient("status-collector", int(API_ID), API_HASH)
update_event = events.UserUpdate()

TLD_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
tlds = []

# Initialize IOC database
db = IOCDatabase()
print("IOC Database initialized successfully!")

req = requests.get(TLD_URL)
# print(req.text)
for line in req.text.splitlines():
    if line and not line.startswith("#"):
        tlds.append(line.strip().lower())

print("TLDs loaded:", len(tlds), "\nFirst TLD:", tlds[0], "\nLast TLD:", tlds[-1])


@client.on(events.NewMessage)
async def handler(event):
    # Get message and sender info
    message_text = event.message.message
    chat_id = event.chat_id
    message_id = event.message.id
    sender_id = event.sender_id
    
    # Get chat and sender details
    chat_title = None
    sender_username = None
    
    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        sender = await event.get_sender()
        sender_username = getattr(sender, 'username', None)
    except Exception as e:
        print(f"Error getting chat/sender info: {e}")
    
    # check if its an IP address or domain name
    regex = r"^(?:(?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])$|^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    words = message_text.split(" ")
    print(f"Processing message from {chat_title}: {words}")
    
    iocs_found = []
    
    for word in words:
        # Check for URLs/links
        if word.startswith("http"):
            print("Link Detected:", word)
            iocs_found.append((word, "url"))
            # Save to database
            if db.save_ioc(word, "url", chat_id, chat_title, message_id, 
                          message_text, sender_id, sender_username):
                print(f"✓ Saved URL to database: {word}")
        
        # Check for IP addresses and domains
        if re.match(regex, word):
            # check if is domain name
            if re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", word):
                # check if domain name ends with a TLD
                domain = word.split(".")[-1].lower()
                if domain in tlds:
                    print("Domain:", word)
                    iocs_found.append((word, "domain"))
                    # Save to database
                    if db.save_ioc(word, "domain", chat_id, chat_title, message_id,
                                  message_text, sender_id, sender_username):
                        print(f"✓ Saved domain to database: {word}")
                else:
                    print("Not a valid TLD:", word)
            else:
                print("IP Address:", word)
                iocs_found.append((word, "ip"))
                # Save to database
                if db.save_ioc(word, "ip", chat_id, chat_title, message_id,
                              message_text, sender_id, sender_username):
                    print(f"✓ Saved IP to database: {word}")
    
    # Print summary if IOCs were found
    if iocs_found:
        print(f"📊 Found {len(iocs_found)} IOC(s) in message from {chat_title}")
        
    await client.send_read_acknowledge(event.chat, event.message)


if __name__ == "__main__":
    print("🚀 Starting IOC Telegram Monitor...")
    print("📊 Database stats:", db.get_stats())
    
    while True:
        try:
            with client:
                client.run_until_disconnected()
        except (KeyboardInterrupt, SystemExit):
            print("\n📊 Final database stats:", db.get_stats())
            print("💾 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            sleep(30)
