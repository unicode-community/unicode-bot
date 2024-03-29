import os

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext

from db.database import Database
from keyboards.community_chats import (
    accept_create_new_chat_and_return_to_menu,
    create_new_chat_and_return_to_menu,
    return_to_menu,
    subscribe_and_return_to_menu,
)
from messages.chats_messages import (
    ask_new_chat_name,
    chats_for_subscriber,
    chats_for_unsubscriber,
    feedback_after_create_new_chat,
    rules_to_create_new_chat,
)
from utils import get_subscription_status
from utils.states import NewChat

router = Router()

@router.callback_query(F.data == "unicode_chats")
async def community_chats(callback: types.CallbackQuery, db: Database, state: FSMContext) -> None:
    await state.clear()

    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    access_to_chats = (
        (subscriber_info["subscription_db_name"] is not None)
        and ("Доступ в основные чаты сообщества" in subscriber_info["subscription_features"])
    )

    if access_to_chats:
        await callback.message.answer(
            text=chats_for_subscriber,
            disable_web_page_preview=True,
            reply_markup=create_new_chat_and_return_to_menu
        )
    else:
        await callback.message.answer(
            text=chats_for_unsubscriber,
            reply_markup=subscribe_and_return_to_menu
        )
    await callback.answer()


@router.callback_query(F.data == "create_new_chat")
async def create_new_chat(callback: types.CallbackQuery) -> None:
    await callback.message.answer(
        text=rules_to_create_new_chat,
        reply_markup=accept_create_new_chat_and_return_to_menu
    )
    await callback.answer()


@router.callback_query(F.data == "accept_create_new_chat")
async def accept_create_new_chat(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        text=ask_new_chat_name,
        reply_markup=return_to_menu
    )
    await state.set_state(NewChat.name)
    await callback.answer()


@router.message(NewChat.name, F.text)
async def finish_create_new_chat(message: types.Message, bot: Bot, state: FSMContext) -> None:
    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"@{message.from_user.username}, `{message.from_user.full_name}` предложил идею для нового чата:\n```\n{message.text}```",
    )
    await message.answer(
        text=feedback_after_create_new_chat,
        reply_markup=return_to_menu
    )

    await state.clear()
