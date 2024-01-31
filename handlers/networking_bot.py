from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import CommandStart
from keyboards.builders import reply_builder
from messages import networkingbot_welcome, link_to_networking_bot
from aiogram.fsm.context import FSMContext


router = Router()

@router.message(F.text == "Бот для IT-знакомств")
async def networking_bot(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        text=networkingbot_welcome,
        reply_markup=reply_builder(
            text=["Перейти в бота", "В главное меню"],
        )
    )
    
    
@router.message(F.text == "Перейти в бота")
async def redirect_networking_bot(message: types.Message) -> None:
    await message.answer(
        text=link_to_networking_bot,
        reply_markup=reply_builder(text=["В главное меню"]),
        disable_web_page_preview=False,
    )