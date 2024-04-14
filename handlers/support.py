from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext

import messages.support as msg
from config import Config
from keyboards import return_to_menu
from utils import Support

router = Router()


@router.callback_query(F.data == "unicode_support")
async def support(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=msg.write_question, reply_markup=return_to_menu)
    await state.set_state(Support.message)
    await callback.answer()


@router.message(Support.message, F.text)
async def support_message(message: types.Message, bot: Bot, state: FSMContext, cfg: Config) -> None:
    await message.answer(text=msg.thanks_for_message, reply_markup=return_to_menu)

    await bot.send_message(
        chat_id=cfg.forwarding_chat,
        text=msg.message_for_admins.format(
            username=message.from_user.username, full_name=message.from_user.full_name, info=message.text
        ),
    )

    await state.clear()
