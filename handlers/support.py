import os

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext

from keyboards.general import return_to_menu
from utils.states import Support

router = Router()

@router.callback_query(F.data == "unicode_support")
async def support(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        text="✍🏻 Пожалуйста, опиши свой вопрос или проблему.",
        reply_markup=return_to_menu
    )
    await state.set_state(Support.message)
    await callback.answer()


@router.message(Support.message, F.text)
async def support_message(message: types.Message, bot: Bot, state: FSMContext) -> None:
    await message.answer(
        text="""💌 Твоё обращение принято! С тобой свяжется модератор, спасибо за доверие к сообществу Unicode! 💜""",
        reply_markup=return_to_menu
    )

    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"@{message.from_user.username}, `{message.from_user.full_name}` обратился в поддержку с сообщением:\n```\n{message.text}```",
    )

    await state.clear()
