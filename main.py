import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from loader import bot, db
from data.config import ADMINS
from handlers.admin import admin_routers       
from handlers.users import users_routers       
from handlers.groups import router as group_router 

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    print("🚀 Bot ishga tushirilmoqda...")
    try:
        await db.connect() 
        await db.create_tables()
        
        print("✅ Baza va Jadvallar tayyor!")
    except Exception as e:
        print(f"❌ Bazaga ulanishda jiddiy xato: {e}")
        return

    dp = Dispatcher()
    dp.include_routers(*admin_routers)
    dp.include_router(group_router)
    dp.include_routers(*users_routers)
    await bot.delete_webhook(drop_pending_updates=True)
    
    print(f"✅ Bot polling rejimida ishlamoqda: @{(await bot.get_me()).username}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi!")