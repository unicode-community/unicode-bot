import logging
import uuid
from datetime import datetime, timedelta

from aiogram import Bot
from pytz import timezone
from yookassa import Payment

from db.database import Database


def create_subscription_params(price: int, return_url: str, user_id: int) -> dict:
    return {
        "amount": {"value": f"{price}.00", "currency": "RUB"},
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": return_url,
        },
        "description": "Оплата подписки на сообщество Unicode",
        "save_payment_method": True,
        "metadata": {"user_id": user_id},
    }


def create_auto_pay_params(price: int, user_id, payment_method_id):
    return {
        "amount": {"value": f"{price}.00", "currency": "RUB"},
        "payment_method_id": payment_method_id,
        "capture": True,
        "description": "Оплата подписки на сообщество Unicode",
        "save_payment_method": True,
        "metadata": {"user_id": user_id, "auto_pay": True},
    }


async def process_auto_pay(bot: Bot, db: Database) -> None:
    users = await db.get_all_users()
    logging.info(datetime.now(tz=timezone("Europe/Moscow")))
    for user in users:
        if user.is_subscriber and (
            datetime.now(tz=timezone("Europe/Moscow")) + timedelta(hours=2) > user.subscription_end
        ):
            pass
            # # print(user)
            # # print(create_auto_pay_params(price=499, user_id=user.tg_id, payment_method_id=user.payment_method_id))
            # idempotence_key = str(uuid.uuid4())
            # payment = Payment.create(
            #     create_auto_pay_params(price=499, user_id=user.tg_id, payment_method_id=user.payment_method_id),
            #     idempotency_key=idempotence_key,
            # )
