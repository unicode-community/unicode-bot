from datetime import datetime, timedelta

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config.buttons import AdditionalButtons, UnicodeButtons
from db.database import Database
from keyboards.general import subscribe_and_return_to_menu
from messages.private_channel import add_for_unsubscribers, private_channel_welcome
from utils.subscriptions import get_subscription_status

router = Router()

@router.callback_query(F.data == "unicode_private_channel")
async def private_channel(callback: types.CallbackQuery, state: FSMContext, db: Database, bot: Bot) -> None:
    await state.clear()

    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    access_to_private_channel = (
        (subscriber_info["subscription_db_name"] is not None)
        and ("Доступ в приватный телеграм канал" in subscriber_info["subscription_features"])
    )

    chat_id = -1002036269871
    expire_date = datetime.now() + timedelta(days=1)
    link = await bot.create_chat_invite_link(chat_id=chat_id, expire_date=expire_date.timestamp(), member_limit=1)

    redirect_to_private_channel_and_return_to_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=AdditionalButtons.redirect_to_private_channel, url=link.invite_link)],
            [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
        ]
    )

    if access_to_private_channel:
        await callback.message.answer(
            text=private_channel_welcome,
            reply_markup=redirect_to_private_channel_and_return_to_menu,
            disable_web_page_preview=True
        )
    else:
        await callback.message.answer(
            text=private_channel_welcome + "\n" + add_for_unsubscribers,
            reply_markup=subscribe_and_return_to_menu,
            disable_web_page_preview=True
        )

    await callback.answer()
