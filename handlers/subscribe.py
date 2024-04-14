import os
import uuid

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from yookassa import Configuration, Payment

import keyboards.subscribe as kb
import messages.subscribe as msg
from config import Config
from db import Database
from keyboards import return_to_menu
from utils import create_subscription_params, get_subscription_status

router = Router()

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


@router.callback_query(F.data == "unicode_subscribe")
async def subscribe(callback: types.CallbackQuery, state: FSMContext, db: Database, cfg: Config) -> None:
    await state.clear()

    subscr_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if subscr_info["is_subscriber"]:
        # СЦЕНАРИИ, КОГДА ЧЕЛ - ПОДПИСЧИК
        txt = msg.already_active_subscr
        if not subscr_info["is_subscribed_to_payments"]:
            # СЦЕНАРИЙ "ЕСЛИ АКТИВНА ВРЕМЕННАЯ ПОДПИСКА"
            txt += "\n\n" + msg.last_active_time_subscr.format(date=subscr_info["subscription_end"].strftime("%d.%m.%Y %H:%M"))
            txt += "\n\n" + msg.add_for_temp_subscr
            payment = Payment.create(
                create_subscription_params(
                    price=cfg.subscription_price, return_url=cfg.bot_link, user_id=callback.from_user.id
                ),
                idempotency_key=str(uuid.uuid4()),
            )
            await callback.message.answer(
                text=txt,
                reply_markup=kb.create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
            )
        else:
            # СЦЕНАРИЙ "ЕСЛИ АКТИВНА ПОСТОЯННАЯ ПОДПИСКА"
            txt += "\n\n" + msg.next_pay_date.format(date=subscr_info["subscription_end"].strftime("%d.%m.%Y %H:%M"))
            await callback.message.answer(text=txt, reply_markup=kb.break_subscr_and_return_to_menu)

    else:
        # СЦЕНАРИЙ, КОГДА У ЧЕЛА НЕТ ПОДПИСКИ
        payment = Payment.create(
            create_subscription_params(
                price=cfg.subscription_price, return_url=cfg.bot_link, user_id=callback.from_user.id
            ),
            idempotency_key=str(uuid.uuid4()),
        )
        await callback.message.answer(
            text=msg.welcome_subscribe,
            reply_markup=kb.create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
            disable_web_page_preview=True,
        )

    await callback.answer()


@router.callback_query(F.data == "break_subscr")
async def break_subscr(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    user_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    await callback.message.answer(
        text=msg.break_subscr.format(date=user_info["subscription_end"].strftime("%d.%m.%Y %H:%M")),
        reply_markup=kb.confirm_break_subscr_and_return_to_menu,
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_break_subscr")
async def confirm_break_subscr(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    await db.user_update(user_id=callback.from_user.id, payment_method_id=None, is_subscribed_to_payments=False)

    await callback.message.answer(text=msg.succesful_break_subscr, reply_markup=return_to_menu)
    await callback.answer()
