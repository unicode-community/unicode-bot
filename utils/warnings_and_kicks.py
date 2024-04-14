import os
import uuid

from aiogram import Bot
from pyairtable import Api
from yookassa import Payment

from config.config import Config
from db.database import Database
from keyboards.subscribe import create_kb_to_payment
from utils.payments import create_subscription_params

api = Api(os.getenv("AIRTABLE_TOKEN"))
table = api.table(os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_ID"))

async def send_warning_7d(bot: Bot, user_id, cfg: Config) -> None:
    try:
        payment = Payment.create(
            create_subscription_params(
                price=cfg.subscription_price, return_url=cfg.bot_link, user_id=user_id
            ),
            idempotency_key=str(uuid.uuid4()),
        )
        await bot.send_message(
            chat_id=user_id,
            text="😰 Скоро срок твоей подписки истекает. Через *7 дней* ты потеряешь доступ ко всем сервисам сообщества Unicode.",
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
        )
    except:
        pass

async def send_warning_1d(bot: Bot, user_id, cfg: Config) -> None:
    try:
        payment = Payment.create(
            create_subscription_params(
                price=cfg.subscription_price, return_url=cfg.bot_link, user_id=user_id
            ),
            idempotency_key=str(uuid.uuid4()),
        )
        await bot.send_message(
            chat_id=user_id,
            text="😰 Завтра срок твоей подписки истекает. Через *24 часа* ты потеряешь доступ ко всем сервисам сообщества Unicode.",
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
        )
    except:
        pass


async def end_subscription_and_kick(bot: Bot, db: Database, user_id, cfg: Config) -> None:
    mentor_info = await db.get_mentor(tg_id=user_id)
    if mentor_info:
        await db.delete_mentor(tg_id=user_id)
        if mentor_info.airtable_record_id:
            table.delete(record_id=mentor_info.airtable_record_id)

    for unicode_chat in cfg.unicode_chat_ids:
        await bot.ban_chat_member(
            chat_id=unicode_chat,
            user_id=user_id,
        )

    await db.user_update(
        user_id=user_id,
        subscription_start=None,
        subscription_end=None,
        is_subscribed_to_payments=None,
        payment_method_id=None,
    )

    try:
        payment = Payment.create(
            create_subscription_params(
                price=cfg.subscription_price, return_url=cfg.bot_link, user_id=user_id
            ),
            idempotency_key=str(uuid.uuid4()),
        )
        await bot.send_message(
            chat_id=user_id,
            text="☠️ Твоя подписка закончилась. Но ты всегда можешь оформить её снова 🌈",
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
        )
    except:
        pass
