import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from dotenv import find_dotenv, load_dotenv
from db.database import Database
import handlers

load_dotenv(find_dotenv())
ALLOWED_UPDATES = ["message", "edited_message"]


async def main() -> None:
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        parse_mode="Markdown"
    )
    dp = Dispatcher()
    db = Database()
    
    dp.startup.register(db.create)
    
    dp.include_routers(
        handlers.commands.router,
        handlers.subscribe.router,
        handlers.knowledge_base.router,
        handlers.mentors_base.router,        
        handlers.community_chats.router,
        handlers.networking_bot.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())