from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from db import Database
from keyboards import main_menu_kb
from messages import main_welcome

router = Router()


@router.callback_query(F.data == "unicode_menu")
async def callback_start_cmd(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(
        text=main_welcome,
        reply_markup=main_menu_kb,
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.message(CommandStart())
async def command_start_cmd(message: types.Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    is_new_user = await db.is_new_user(tg_id=message.from_user.id)
    if is_new_user:
        await db.new_user(tg_id=message.from_user.id, tg_username=message.from_user.username)
    await message.answer(
        text=main_welcome,
        reply_markup=main_menu_kb,
        disable_web_page_preview=True,
    )
