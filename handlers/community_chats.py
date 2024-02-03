from datetime import datetime

from aiogram import F, Router, types

from db.database import Database
from keyboards.builders import reply_builder
from messages import active_chats, active_chats_no_links, error_no_subscr_for_chats

router = Router()

@router.message(F.text.lower() == "чаты сообщества")
async def community_chats(message: types.Message, db: Database) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    if is_subscriber:
        await message.answer(
            text=active_chats,
            disable_web_page_preview=True,
            reply_markup=reply_builder(["В главное меню", "Оформить подписку"])
        )
    else:
        await message.answer(text=error_no_subscr_for_chats)
        await message.answer(text=active_chats_no_links)
