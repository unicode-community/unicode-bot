from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import CommandStart
from keyboards.builders import reply_builder
from messages import active_chats, active_chats_no_links, error_no_subscr_for_chats
from db.database import Database
from datetime import datetime, timedelta

router = Router()

@router.message(F.text.lower() == "оформить подписку")
async def subscribe(message: types.Message, db: Database) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    if is_subscriber:
        await message.answer(
            text="Твоя подписка активна. Пользуйся ей с умом...",
            reply_markup=reply_builder(["В главное меню"])
        )
    else:
        await message.answer(
            text="Пожалуйста, выбери тип подписки, который тебя интересует",
            reply_markup=reply_builder(text=["Unicode Base (499 ₽/мес)"])
        )


@router.message(F.text == "Unicode Base (499 ₽/мес)")
async def base_subscription(message: types.Message, db: Database) -> None:
    await message.answer(
        text="⚠️⚠️⚠️ ЗАГЛУШКА. ТУТ БУДЕТ ПРОЦЕСС ОПЛАТЫ" # TODO fix this
    )

    if 1: # TODO проверка, что оплата прошла успешно
        subscriber_info = {
            "tg_id": message.from_user.id,
            "subscription_type": "base",
            "subscription_start": datetime.now(),
            "subscription_end": datetime.now() + timedelta(days=30)
        }

        await db.new_subscriber(**subscriber_info)

        await message.answer(
            text="Оплата прошла успешно! Добро пожаловать в Unicode 💜!",
            reply_markup=reply_builder(text=["В главное меню"])
        )
    else:
        await message.answer(
            text="Произошла ошибка при оплате",
            reply_markup=reply_builder(text=["В главное меню"])
        )