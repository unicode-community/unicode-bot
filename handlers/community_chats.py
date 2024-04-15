import uuid

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from yookassa import Payment

import keyboards.community_chats as kb
import messages.community_chats as msg
from config import Config
from db import Database
from filters import ChatTypeFilter
from keyboards import create_kb_to_payment, return_to_menu
from utils import NewChat, create_subscription_params, get_subscription_status

router = Router()
router.message.filter(ChatTypeFilter(chat_type="private"))


@router.callback_query(F.data == "unicode_chats")
async def community_chats(callback: types.CallbackQuery, db: Database, state: FSMContext, cfg: Config) -> None:
    await state.clear()

    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if subscriber_info["is_subscriber"]:
        await callback.message.answer(
            text=msg.chats_for_subscriber,
            disable_web_page_preview=True,
            reply_markup=kb.create_new_chat_and_return_to_menu,
        )
    else:
        payment = Payment.create(
            create_subscription_params(
                price=cfg.subscription_price, return_url=cfg.bot_link, user_id=callback.from_user.id
            ),
            idempotency_key=str(uuid.uuid4()),
        )
        await callback.message.answer(
            text=msg.chats_for_unsubscriber,
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
        )
    await callback.answer()


@router.callback_query(F.data == "create_new_chat")
async def create_new_chat(callback: types.CallbackQuery) -> None:
    await callback.message.answer(
        text=msg.rules_to_create_new_chat, reply_markup=kb.accept_create_new_chat_and_return_to_menu
    )
    await callback.answer()


@router.callback_query(F.data == "accept_create_new_chat")
async def accept_create_new_chat(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=msg.ask_new_chat_name, reply_markup=return_to_menu)
    await state.set_state(NewChat.name)
    await callback.answer()


@router.message(NewChat.name, F.text)
async def finish_create_new_chat(message: types.Message, bot: Bot, state: FSMContext, cfg: Config) -> None:
    await bot.send_message(
        chat_id=cfg.forwarding_chat,
        text=msg.message_for_admins.format(
            username=message.from_user.username, full_name=message.from_user.full_name, info=message.text
        ),
    )
    await message.answer(text=msg.feedback_after_create_new_chat, reply_markup=return_to_menu)

    await state.clear()
