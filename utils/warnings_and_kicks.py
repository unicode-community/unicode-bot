from datetime import datetime, timedelta

from aiogram import Bot

from db.database import Database
from keyboards.general import subscribe_and_return_to_menu


async def send_warnings_and_kicks(bot: Bot, db: Database) -> None:
    users = await db.get_all_users()

    for user in users:
        if (user.subscription_db_name is not None) and (datetime.now() > user.subscription_end):
            # TODO кик из чатов и из таблицы менторов
            await db.user_update(
                user_id=user.tg_id,
                subscription_db_name=None,
                subscription_start=None,
                subscription_end=None,
                is_subscribed_to_payments=None,
                payment_method_id=None
            )
            try:
                await bot.send_message(
                    chat_id=user.tg_id,
                    text="☠️ Твоя подписка закончилась. Но ты всегда можешь оформить её снова 🌈",
                    reply_markup=subscribe_and_return_to_menu
                )
            except:
                # TODO обработать ошибку
                pass
        elif (user.subscription_db_name is not None) and (user.send_warning is None) and ((datetime.now() + timedelta(days=1) > user.subscription_end)):
            try:
                await bot.send_message(
                    chat_id=user.tg_id,
                    text="😰 Завтра срок твоей подписки истекает. Через *24 часа* ты потеряешь доступ ко всем сервисам сообщества Unicode.",
                    reply_markup=subscribe_and_return_to_menu
                )
                await db.user_update(user_id=user.tg_id, send_warning=True)
            except:
                # TODO обработать ошибку
                pass
