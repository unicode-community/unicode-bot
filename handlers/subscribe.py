import os
import uuid
from datetime import datetime, timedelta

import pytz
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv
from icecream import ic
from yookassa import Configuration, Payment

import keyboards.subscribe as keyboards
from db.database import Database
from keyboards.general import return_to_menu, write_to_support_and_return_to_menu
from keyboards.subscribe import create_kb_to_payment
from messages import subscribe as messages
from utils import get_subscription_status
from utils.payments import unicode_base_params, unicode_guest_params, unicode_starter_params
from utils.subscriptions import match_subscription, unicode_base, unicode_guest, unicode_starter

router = Router()
load_dotenv(find_dotenv())

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


@router.callback_query(F.data == "unicode_subscribe")
async def subscribe(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    subscr_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if subscr_info["is_subscriber"]:
        txt = messages.welcome_subscribe
        txt += "\n\n" + messages.current_subscr.format(
            subscr=match_subscription[subscr_info["subscription_db_name"]].name,
            price=match_subscription[subscr_info["subscription_db_name"]].price
        )
        if not subscr_info["is_subscribed_to_payments"]:
            txt += "\n\n" + messages.last_active_time_subscr.format(date=subscr_info["subscription_end"].strftime("%d.%m.%Y %H:%M"))
            txt += "\n\n" + messages.choice_type_subscr
        else:
            txt += "\n\n" + messages.choice_update_or_break_subscr

        if not subscr_info["is_subscribed_to_payments"]:
            await callback.message.answer(
                text=txt,
                reply_markup=keyboards.choice_subscr_type_and_return_to_menu
            )
        else:
            await callback.message.answer(
                text=txt,
                reply_markup=keyboards.choice_subscr_type_and_break_subscr_and_return_to_menu
            )

    else:
        await callback.message.answer(
            text=messages.welcome_subscribe + "\n\n" + messages.choice_type_subscr,
            reply_markup=keyboards.choice_subscr_type_and_return_to_menu
        )

    await callback.answer()


@router.callback_query(F.data == "unicode_guest")
async def pay_unicode_guest(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    subscr_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if (subscr_info["subscription_db_name"] == "unicode_guest") and (subscr_info["is_subscribed_to_payments"]):
        await callback.message.answer(
            text=messages.already_activated_subscr,
            reply_markup=return_to_menu
        )
    else:
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(unicode_guest_params, idempotence_key)

        await callback.message.answer(
            text=messages.unicode_guest_info,
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id)
        )
    await callback.answer()


@router.callback_query(F.data == "unicode_starter")
async def pay_unicode_starter(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    subscr_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if (subscr_info["subscription_db_name"] == "unicode_starter") and (subscr_info["is_subscribed_to_payments"]):
        await callback.message.answer(
            text=messages.already_activated_subscr,
            reply_markup=return_to_menu
        )
    else:
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(unicode_starter_params, idempotence_key)

        await callback.message.answer(
            text=messages.unicode_starter_info,
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id)
        )
    await callback.answer()


@router.callback_query(F.data == "unicode_base")
async def pay_unicode_base(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    subscr_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if (subscr_info["subscription_db_name"] == "unicode_base") and (subscr_info["is_subscribed_to_payments"]):
        await callback.message.answer(
            text=messages.already_activated_subscr,
            reply_markup=return_to_menu
        )
    else:
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(unicode_base_params, idempotence_key)

        await callback.message.answer(
            text=messages.unicode_base_info,
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id)
        )
    await callback.answer()


@router.callback_query(F.data == "break_subscr")
async def break_subscr(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    user_info = await db.get_user(user_id=callback.from_user.id)

    subscr_end_date = user_info.subscription_end.strftime("%d.%m.%Y %H:%M")

    await callback.message.answer(
        text=messages.break_subscr.format(date=subscr_end_date),
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
async def check_payment(callback: types.CallbackQuery, db: Database) -> None:
    payment_id = callback.data.split("_")[2]
    payment = Payment.find_one(payment_id)
    # ic(payment.json())
    if payment.status == "succeeded":
        try:
            user_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)
            if user_info["subscription_db_name"] == payment.metadata["subscription_db_name"]:
                subscription_end = user_info["subscription_end"] + timedelta(days=30)
            else:
                subscription_end = datetime.now() + timedelta(days=30)
            subscriber_info = {
                "tg_id": callback.from_user.id,
                "subscription_db_name": payment.metadata["subscription_db_name"],
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
            await callback.message.answer(
                text=messages.error_pay_subscr,
                reply_markup=write_to_support_and_return_to_menu
            )
            ic(err)

        formatting_subscription_name = ""
        for subscr in [unicode_guest, unicode_base, unicode_starter]:
            if payment.metadata["subscription_db_name"] == subscr.db_name:
                formatting_subscription_name = f"{subscr.name} ({subscr.price} ₽/мес)"

        await callback.message.answer(
            text=f"@{callback.from_user.username}, `{callback.from_user.full_name}` оформил подписку `{formatting_subscription_name}`",
        )
        # TODO поставить отправку в админ чат
        # await bot.send_message(
            # chat_id=os.getenv("FORWADING_CHAT"),
            # text=f"@{callback.from_user.username}, `{callback.from_user.full_name}` оформил подписку `{formatting_subscription_name}`",
        # )
    elif payment.status == "canceled":
        await callback.message.delete()
        await callback.message.answer(
            text="🚫 Оплата отменена! Вы отменили платеж самостоятельно, истекло время на принятие платежа или платеж был отклонен ЮKassa или платежным провайдером.",
            reply_markup=write_to_support_and_return_to_menu
        )
    elif payment.status == "pending":
        await callback.answer(
            text="⏳ Платеж создан и ожидает действий от пользователя."
        )
    await callback.answer()
