from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from keyboards.reply import start_kb
from messages import main_welcome

router = Router()

@router.message(Command("menu"))
@router.message(F.text.lower() == "в главное меню")
@router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=main_welcome,
        reply_markup=start_kb,
    )
