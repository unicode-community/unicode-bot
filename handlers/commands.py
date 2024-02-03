from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards.builders import reply_builder
from messages import main_welcome

router = Router()

@router.message(F.text.lower() == "в главное меню")
@router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=main_welcome,
        reply_markup=reply_builder(
            text=["Оформить подписку", "База вопросов", "Бот для IT-знакомств", "База менторов", "Чаты сообщества"],
            sizes=[1, 2, 2]
        )
    )
