import logging
import os
from datetime import datetime, timedelta

from aiogram import Bot
from fastapi import Depends, FastAPI, HTTPException, Request
from icecream import ic
from pytz import timezone

import messages.subscribe as msg
from config import cfg
from db import Database, get_db
from keyboards import return_to_menu
from utils import get_subscription_status

app = FastAPI()
bot = Bot(token=os.getenv("BOT_TOKEN"))


@app.get("/subscribers/{tg_id}")
async def check_subscription_status(tg_id: int, db: Database = Depends(get_db)):
    return await get_subscription_status(user_tg_id=tg_id, db=db)


@app.post("/pay/yookassa")
async def check_pay_yookassa(request: Request, db: Database = Depends(get_db)):
    data = await request.json()
    ic(data)
    if data["object"]["status"] != "succeeded":
        raise HTTPException(200)
    payment_object = data["object"]
    logging.info(payment_object)
    user_id = int(payment_object["metadata"]["user_id"])
    user_info = await get_subscription_status(user_tg_id=user_id, db=db)

    now_time = datetime.now(tz=timezone("Europe/Moscow"))

    if (user_info["subscription_start"] is not None) and (now_time >= user_info["subscription_start"]):
        subscription_start = user_info["subscription_start"]
    else:
        subscription_start = now_time

    if (user_info["subscription_end"] is not None) and (now_time <= user_info["subscription_end"]):
        subscription_end = user_info["subscription_end"] + timedelta(days=30)
    else:
        subscription_end = now_time + timedelta(days=30)

    subscriber_info = {
        "tg_id": user_id,
        "is_subscriber": True,
        "subscription_start": subscription_start,
        "subscription_end": subscription_end,
        "payment_method_id": payment_object["payment_method"]["id"],
        "is_subscribed_to_payments": True,
    }

    await db.user_update(user_id=user_id, **subscriber_info)

    user = await db.get_user(user_id=user_id)

    if "auto_pay" in payment_object["metadata"]:
        await bot.send_message(chat_id=user_id, text=msg.successful_extend_subscr, reply_markup=return_to_menu)

        await bot.send_message(
            chat_id=cfg.forwarding_chat,
            text=msg.extend_subscription_for_admins.format(
                username=user.tg_username,
                price=data["object"]["amount"]["value"],
            ),
        )
    else:
        await bot.send_message(chat_id=user_id, text=msg.successful_pay_subscr, reply_markup=return_to_menu)

        await bot.send_message(
            chat_id=cfg.forwarding_chat,
            text=msg.new_subscriber_for_admins.format(
                username=user.tg_username,
                price=data["object"]["amount"]["value"],
            ),
        )
    raise HTTPException(200)
