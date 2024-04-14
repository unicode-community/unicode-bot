import asyncio
import logging
import os

import yaml
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import find_dotenv, load_dotenv

import handlers
from config.buttons import UnicodeButtons
from config.config import cfg
from db.database import Database
from utils import process_auto_pay, send_warnings_and_kicks

ALLOWED_UPDATES = ["message", "edited_message"]


async def main() -> None:
    load_dotenv(find_dotenv(filename=".env"))
    bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode="Markdown")
    bot.admins_list = cfg.admins_ids
    dp = Dispatcher()
    db = Database()

    dp.startup.register(db.create)

    dp.include_routers(
        handlers.commands.router,
        handlers.subscribe.router,
        handlers.knowledge_base.router,
        handlers.mentors_table.router,
        handlers.community_chats.router,
        # handlers.networking_bot.router,
        handlers.support.router,
        handlers.admin.router,
    )
    jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite"), "memory": MemoryJobStore()}
    scheduler = AsyncIOScheduler(jobstores=jobstores)
    scheduler.add_job(
        send_warnings_and_kicks,
        trigger="interval",
        hours=1,
        kwargs={"bot": bot, "db": db, "cfg": cfg},
        jobstore="memory",
    )
    scheduler.add_job(
        process_auto_pay, trigger="interval", seconds=10, kwargs={"bot": bot, "db": db}, jobstore="memory"
    )
    # scheduler.start()

    await bot.set_my_commands(commands=[BotCommand(command="start", description=UnicodeButtons.main_menu)])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db, cfg=cfg)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
