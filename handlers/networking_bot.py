import uuid

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from yookassa import Payment

from db.database import Database
from keyboards.networking_bot import redirect_to_bot_and_return_to_menu
from keyboards.subscribe import (
    create_kb_to_payment,
)
from messages.networking_bot import add_for_unsubscribers, welcome_networking_bot
from utils import get_subscription_status
from utils.payments import create_subscription_params

router = Router()

@router.callback_query(F.data == "unicode_networking")
async def networking_bot(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()
    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if subscriber_info["is_subscriber"]:
        await callback.message.answer(
            text=welcome_networking_bot,
            reply_markup=redirect_to_bot_and_return_to_menu
        )
    else:
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(create_subscription_params(price=499, user_id=callback.from_user.id), idempotency_key=idempotence_key)
        await callback.message.answer(
            text=welcome_networking_bot + "\n" + add_for_unsubscribers,
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
        )
    await callback.answer()
