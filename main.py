from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from flask import Flask
import threading
import os
from config import API_TOKEN
from database import init_db, close_db
from plugins import start_router, settings_router, video_router, admin_router, caption_router
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start_router)
dp.include_router(settings_router)
dp.include_router(caption_router)
dp.include_router(video_router)
dp.include_router(admin_router)

# Flask health check server
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot Made By @Sujan_BotZ"
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
async def main():
    # Initialize database
    await init_db()
    print("🚀 Bot is starting...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()

if __name__ == "__main__":
    print(r"""
███████╗██╗   ██╗     ██╗ █████╗ ███╗   ██╗        ██████╗  ██████╗ ████████╗███████╗
██╔════╝██║   ██║     ██║██╔══██╗████╗  ██║        ██╔══██╗██╔═══██╗╚══██╔══╝╚══███╔╝
███████╗██║   ██║     ██║███████║██╔██╗ ██║        ██████╔╝██║   ██║   ██║     ███╔╝ 
╚════██║██║   ██║██   ██║██╔══██║██║╚██╗██║        ██╔══██╗██║   ██║   ██║    ███╔╝  
███████║╚██████╔╝╚█████╔╝██║  ██║██║ ╚████║███████╗██████╔╝╚██████╔╝   ██║   ███████╗
╚══════╝ ╚═════╝  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═════╝  ╚═════╝    ╚═╝   ╚══════╝                                                     
      BOT WORKING PROPERLY....
    """)
    print("Starting Bot...")
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
