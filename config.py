# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
import os
import random

API_TOKEN = os.environ.get("API_TOKEN", "") #required


MONGO_URL = os.environ.get("MONGO_URL", "") #required
DB_NAME = "thumbnail_bot"
OWNER_ID = int(os.environ.get("OWNER_ID", "")) # Owner/Admin
# UI URLs - Multiple images that rotate randomly
# Use DIRECT image URLs (https://i.ibb.co/...) not page URLs (https://ibb.co/...)
START_PICS = [
    "https://i.ibb.co/0jjgxKM4/changli-wuthering-waves-4k-wallpaper-uhdpaper-com-437-2-b.jpg",
    # Add more direct image URLs here
]
CHANNEL_URL = os.environ.get("CHANNEL_URL", "https://t.me/Sujan_BotZ")
DEV_URL = os.environ.get("DEV_URL", "https://t.me/Sujan_Ch")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))  # e.g., -100xxxxxxxxxxxx

def get_random_pic() -> str:
    """Get a random image from START_PICS."""
    if START_PICS:
        return random.choice(START_PICS)
    return None

