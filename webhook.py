import logging
import os
import uuid
from datetime import timedelta, datetime

from aiogram import Bot
from fastapi import Depends, FastAPI, Request, HTTPException
from yookassa import Payment

from db.database import Database, get_db
from utils.subscriptions import get_subscription_status
from keyboards.general import return_to_menu
from messages import subscribe as subscribe_messages

app = FastAPI()
bot = Bot(
    token=os.getenv("BOT_TOKEN")
)


@app.get("/subscribers/{tg_id}")
async def check_subscription_status(tg_id: int, db: Database = Depends(get_db)):
    return await get_subscription_status(user_tg_id=tg_id, db=db)


@app.post('/pay/yookassa')
async def check_pay_yookassa(request: Request, db: Database = Depends(get_db)):
    data = await request.json()
    if data["object"]["status"] != "succeeded":
        raise HTTPException(200)
    payment_object = data["object"]
    logging.info(payment_object)
    user_id = int(payment_object["metadata"]["user_id"])
    user_info = await get_subscription_status(user_tg_id=user_id, db=db)
    if (user_info["subscription_end"] is not None) and (datetime.now() <= user_info["subscription_end"]):
        subscription_end = user_info["subscription_end"] + timedelta(days=30)
    else:
        subscription_end = datetime.now() + timedelta(days=30)
    subscriber_info = {
        "tg_id": user_id,
        "is_subscriber": True,
        "subscription_start": datetime.now(),
        "subscription_end": subscription_end,
        "payment_method_id": payment_object["payment_method"]["id"],
        "is_subscribed_to_payments": True
    }

    await db.user_update(user_id=user_id, **subscriber_info)
    user = await db.get_user(user_id)
    if "auto_pay" in payment_object["metadata"]:
        text = "Подписка продлена автоматически!"
        admin_text = f"Подписчик @{user.tg_username} получена автоплата\n" \
                     f"Цена: {data['object']['amount']['value']} руб\n" \
                     f"Период оплаты: 30 дней"
    else:
        text = subscribe_messages.successful_pay_subscr
        admin_text = f"У вас появился новый подписчик @{user.tg_username}\n" \
                     f"Цена: {data['object']['amount']['value']} руб\n" \
                     f"Период оплаты: 30 дней"
    await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=return_to_menu
    )

    try:
        await bot.send_message(
            chat_id=os.getenv("FORWADING_CHAT"),
            text=admin_text
        )
    except:
        pass
    raise HTTPException(200)
