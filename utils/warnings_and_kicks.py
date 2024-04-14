import uuid
from datetime import datetime, timedelta

from aiogram import Bot
from pytz import timezone
from yookassa import Payment

from config.cfg import Config
from db.database import Database
from keyboards.subscribe import create_kb_to_payment
from utils.payments import create_subscription_params


async def send_warnings_and_kicks(bot: Bot, db: Database, cfg: Config) -> None:
    users = await db.get_all_users()

    for user in users:
        if (user.is_subscriber) and (datetime.now(tz=timezone("Europe/Moscow")) > user.subscription_end):
            # TODO кик из чатов и из таблицы менторов
            await db.user_update(
                user_id=user.tg_id,
                subscription_start=None,
                subscription_end=None,
                is_subscribed_to_payments=None,
                payment_method_id=None,
            )
            try:
                idempotence_key = str(uuid.uuid4())
                payment = Payment.create(
                    create_subscription_params(
                        price=cfg.subscription_price, return_url=cfg.bot_link, user_id=user.tg_id
                    ),
                    idempotency_key=idempotence_key,
                )
                await bot.send_message(
                    chat_id=user.tg_id,
                    text="☠️ Твоя подписка закончилась. Но ты всегда можешь оформить её снова 🌈",
                    reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
                )
            except:
                # TODO обработать ошибку
                pass
        elif (
            (user.is_subscriber)
            and (user.send_warning is None)
            and ((datetime.now(tz=timezone("Europe/Moscow")) + timedelta(days=1)) > user.subscription_end)
        ):
            try:
                idempotence_key = str(uuid.uuid4())
                payment = Payment.create(
                    create_subscription_params(
                        price=cfg.subscription_price, return_url=cfg.bot_link, user_id=user.tg_id
                    ),
                    idempotency_key=idempotence_key,
                )
                await bot.send_message(
                    chat_id=user.tg_id,
                    text="😰 Завтра срок твоей подписки истекает. Через *24 часа* ты потеряешь доступ ко всем сервисам сообщества Unicode.",
                    reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
                )
                await db.user_update(user_id=user.tg_id, send_warning=True)
            except:
                # TODO обработать ошибку
                pass
