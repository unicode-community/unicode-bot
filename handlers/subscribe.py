import logging
import os
import uuid
from datetime import datetime, timedelta

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv
from icecream import ic
from yookassa import Configuration, Payment

import keyboards.subscribe as keyboards
from db.database import Database
from keyboards.general import return_to_menu
from messages import subscribe as messages
from utils import get_subscription_status
from utils.payments import create_subscription_params

router = Router()
load_dotenv(find_dotenv())

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


@router.callback_query(F.data == "unicode_subscribe")
async def subscribe(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    subscr_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if subscr_info["is_subscriber"]:
        # СЦЕНАРИИ, КОГДА ЧЕЛ - ПОДПИСЧИК
        txt = messages.already_active_subscr
        if not subscr_info["is_subscribed_to_payments"]:
            # СЦЕНАРИЙ "ЕСЛИ АКТИВНА ВРЕМЕННАЯ ПОДПИСКА"
            txt += "\n\n" + messages.last_active_time_subscr.format(date=subscr_info["subscription_end"].strftime("%d.%m.%Y %H:%M"))
            txt += "\n\n" + messages.add_for_temp_subscr
            idempotence_key = str(uuid.uuid4())
            payment = Payment.create(create_subscription_params(price=499, user_id=callback.from_user.id), idempotency_key=idempotence_key)
            await callback.message.answer(
                text=txt,
                reply_markup=keyboards.create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id)
            )
        else:
            # СЦЕНАРИЙ "ЕСЛИ АКТИВНА ПОСТОЯННАЯ ПОДПИСКА"
            txt += "\n\n" + messages.next_pay_date.format(date=subscr_info["subscription_end"].strftime("%d.%m.%Y %H:%M"))
            await callback.message.answer(
                text=txt,
                reply_markup=keyboards.break_subscr_and_return_to_menu
            )

    else:
        # СЦЕНАРИЙ, КОГДА У ЧЕЛА НЕТ ПОДПИСКИ
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(create_subscription_params(price=499, user_id=callback.from_user.id), idempotency_key=idempotence_key)
        await callback.message.answer(
            text=messages.welcome_subscribe,
            reply_markup=keyboards.create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
            disable_web_page_preview=True
        )

    await callback.answer()


@router.callback_query(F.data == "break_subscr")
async def break_subscr(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    user_info = await db.get_user(user_id=callback.from_user.id)

    await callback.message.answer(
        text=messages.break_subscr.format(date=user_info.subscription_end.strftime("%d.%m.%Y %H:%M")),
        reply_markup=keyboards.confirm_break_subscr_and_return_to_menu
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_break_subscr")
async def confirm_break_subscr(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    await db.user_update(
        user_id=callback.from_user.id,
        **{"payment_method_id": None, "is_subscribed_to_payments": False}
    )

    await callback.message.answer(
        text=messages.succesful_break_subscr,
        reply_markup=return_to_menu
    )
    await callback.answer()


@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment(callback: types.CallbackQuery, db: Database, bot: Bot) -> None:
    payment_id = callback.data.split("_")[2]
    payment = Payment.find_one(payment_id)
    if payment.status == "succeeded":
        try:
            user_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)
            if (user_info["subscription_end"] is not None) and (datetime.now() <= user_info["subscription_end"]):
                subscription_end = user_info["subscription_end"] + timedelta(days=30)
            else:
                subscription_end = datetime.now() + timedelta(days=30)
            subscriber_info = {
                "tg_id": callback.from_user.id,
                "is_subscriber": True,
                "subscription_start": datetime.now(),
                "subscription_end": subscription_end,
                "payment_method_id": payment.payment_method.id,
                "is_subscribed_to_payments": True
            }

            await db.user_update(user_id=callback.from_user.id, **subscriber_info)

            await callback.message.delete()
            await callback.message.answer(
                text=messages.successful_pay_subscr,
                reply_markup=return_to_menu
            )
        except Exception as err:
            idempotence_key = str(uuid.uuid4())
            payment = Payment.create(create_subscription_params(price=499, user_id=callback.from_user.id), idempotency_key=idempotence_key)

            await callback.message.answer(
                text=messages.error_pay_subscr,
                reply_markup=keyboards.create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id, add_write_support=True)
            )
            ic(err) # TODO заменить на логирование

        await bot.send_message(
            chat_id=os.getenv("FORWADING_CHAT"),
            text=f"У вас появился новый подписчик @{callback.from_user.username}, {callback.from_user.full_name}\n"
            f"Цена: {payment.amount.value} руб\n"
            f"Период оплаты: 30 дней"
        )
    elif payment.status == "canceled":
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(create_subscription_params(price=499, user_id=callback.from_user.id), idempotency_key=idempotence_key)

        await callback.message.delete()
        await callback.message.answer(
            text="🚫 Оплата отменена! Вы отменили платеж самостоятельно, истекло время на принятие платежа или платеж был отклонен ЮKassa или платежным провайдером.",
            reply_markup=keyboards.create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id, add_write_support=True)
        )
    elif payment.status == "pending":
        await callback.answer(
            text="⏳ Платеж создан и ожидает действий от пользователя."
        )
    await callback.answer()
