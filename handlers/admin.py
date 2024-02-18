from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db.database import Database
from filters.filters import IsAdmin
from keyboards.builders import reply_builder
from utils.states import Subscription

router = Router()
router.message.filter(IsAdmin())


ADMIN_KB = reply_builder(
    text=["Отменить подписку (админ версия)", "В главное меню"],
    sizes=[1, 1]
)


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    await message.answer(
        text="Что хочешь сделать?",
        reply_markup=ADMIN_KB
    )


@router.message(F.text == "Отменить подписку (админ версия)")
async def unsubscribe_admin(message: types.Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    if not is_subscriber:
        await message.answer(
            text="В данный момент у тебя нет активной подписки.",
            reply_markup=reply_builder(["В главное меню"])
        )
    else:
        await db.unsubscribe_user(tg_id=message.from_user.id)
        await message.answer(
            text="Ты уверен, что хочешь отменить свою подписку?",
            reply_markup=reply_builder(["Да (админ версия)", "В главное меню"], sizes=[1, 1])
        )
        await state.set_state(Subscription.confirm_delete)


@router.message(Subscription.confirm_delete, F.text == "Да (админ версия)")
async def confirm_unsubscribe(message: types.Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    await db.unsubscribe_user(tg_id=message.from_user.id)
    await message.answer(
        text="Твоя подписка успешно отменена!",
        reply_markup=reply_builder(["В главное меню"])
    )
