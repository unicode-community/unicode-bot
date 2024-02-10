from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from db.database import Database
from keyboards.builders import reply_builder
from keyboards.inline import redirect_networking_bot
from messages import networkingbot_welcome

router = Router()

@router.message(F.text == "Бот для IT-знакомств")
async def networking_bot(message: types.Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if is_subscriber:
        await message.answer(
            text="🦄",
            reply_markup=reply_builder(["В главное меню"])
        )
        await message.answer(
            text=networkingbot_welcome,
            reply_markup=redirect_networking_bot
        )
    else:
        await message.answer(
            text="Извините, но доступ к боту для знакомств есть только у подписчиков сообщества",
            reply_markup=reply_builder(["Оформить подписку", "В главное меню"], sizes=[1, 1])
        )
