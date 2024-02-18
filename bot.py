import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import find_dotenv, load_dotenv

import handlers
from db.database import Database

load_dotenv(find_dotenv())
ALLOWED_UPDATES = ["message", "edited_message"]


async def main() -> None:
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        parse_mode="Markdown"
    )
    bot.admins_list = [int(os.getenv("ADMIN_ID")), int(os.getenv("DEV_ID"))]
    dp = Dispatcher()
    db = Database()

    dp.startup.register(db.create)

    dp.include_routers(
        handlers.commands.router,
        handlers.subscribe.router,
        handlers.knowledge_base.router,
        handlers.mentors_base.router,
        handlers.community_chats.router,
        handlers.networking_bot.router,
        handlers.admin.router
    )

    await bot.set_my_commands(commands=[BotCommand(command="menu", description="⚙️ Главное меню")])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
