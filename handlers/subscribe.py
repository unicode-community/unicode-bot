import os
import uuid
from datetime import datetime, timedelta

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv

# from icecream import ic
from yookassa import Configuration, Payment

from db.database import Database
from keyboards.builders import reply_builder
from keyboards.inline import create_kb_to_payment
from messages import (
    cancel_subscription,
    subscription_type_info,
    subscription_type_info_with_time,
    subscriptions_welcome,
    unicode_base_info,
    unicode_guest_info,
)
from utils.payments import unicode_base_params, unicode_guest_params
from utils.states import Subscription

router = Router()
load_dotenv(find_dotenv())

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


subscriptions = {
    "unicode_guest": "👤 Unicode Guest (99 ₽/мес)",
    "unicode_base": "🟣 Unicode Base (499 ₽/мес)"
}

@router.message(F.text.lower() == "подписка")
async def subscribe(message: types.Message, db: Database, state: FSMContext):
    await state.clear()
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if is_subscriber:
        if user_info.is_subscribed_to_payments:
            await message.answer(
                text=subscription_type_info.format(
                    subscription_type=subscriptions[user_info.subscription_type]
                ),
                reply_markup=reply_builder(["Изменить подписку", "Отменить подписку", "В главное меню"], sizes=[2, 1])
            )
        else:
            await message.answer(
                text=subscription_type_info_with_time.format(
                    subscription_type=subscriptions[user_info.subscription_type],
                    subscription_end=user_info.subscription_end.strftime("%d.%m.%Y %H:%M")
                ),
                reply_markup=reply_builder(["Продлить подписку", "В главное меню"], sizes=[1, 1])
            )
    else:
        await message.answer(
            text="🚫 В данный момент у тебя нет активной подписки.",
            reply_markup=reply_builder(["Оформить подписку", "В главное меню"], sizes=[1, 1])
        )


@router.message(F.text == "Изменить подписку")
async def change_subscription_type(message: types.Message, state: FSMContext):
    await message.answer(
        text=subscriptions_welcome,
        reply_markup=reply_builder(text=["👤 Unicode Guest (99 ₽/мес)", "🟣 Unicode Base (499 ₽/мес)", "В главное меню"], sizes=[2, 1])
    )

    await state.set_state(Subscription.change_subscription)


@router.message(Subscription.change_subscription, F.text == "👤 Unicode Guest (99 ₽/мес)")
async def change_subscription_guest(message: types.Message, db: Database, state: FSMContext):
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    if message.text == subscriptions[user_info.subscription_type]:
        await message.answer(
            text="✅ Данный вид подписки уже активирован.",
            reply_markup=reply_builder(["В главное меню"])
        )
    else:
        await message.answer(
            text="🦄",
            reply_markup=reply_builder(["В главное меню"])
        )

        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(unicode_guest_params, idempotence_key)

        await message.answer(
            text=unicode_guest_info,
            reply_markup=create_kb_to_payment(
                url=payment.confirmation.confirmation_url,
                payment_id=payment.id,
                subscription_type="👤 Unicode Guest"
            )
        )
    await state.clear()


@router.message(Subscription.change_subscription, F.text == "🟣 Unicode Base (499 ₽/мес)")
async def change_subscription_base(message: types.Message, db: Database, state: FSMContext):
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    if message.text == subscriptions[user_info.subscription_type]:
        await message.answer(
            text="✅ Данный вид подписки уже активирован.",
            reply_markup=reply_builder(["В главное меню"])
        )
    else:
        await message.answer(
            text="🦄",
            reply_markup=reply_builder(["В главное меню"])
        )

        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(unicode_base_params, idempotence_key)

        await message.answer(
            text=unicode_base_info,
            reply_markup=create_kb_to_payment(
                url=payment.confirmation.confirmation_url,
                payment_id=payment.id,
                subscription_type="🟣 Unicode Base"
            )
        )
    await state.clear()


@router.message(F.text == "Продлить подписку")
async def extend_subscription(message: types.Message, state: FSMContext):
    #TODO сделать проверку что чел может продлевать
    await message.answer(
        text=subscriptions_welcome,
        reply_markup=reply_builder(text=["👤 Unicode Guest (99 ₽/мес)", "🟣 Unicode Base (499 ₽/мес)", "В главное меню"], sizes=[2, 1])
    )
    await state.set_state(Subscription.extend_subscription)


@router.message(Subscription.extend_subscription, F.text == "👤 Unicode Guest (99 ₽/мес)")
async def extend_subscription_guest(message: types.Message, state: FSMContext):
    await message.answer(
        text="🦄",
        reply_markup=reply_builder(["В главное меню"])
    )

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(unicode_guest_params, idempotence_key)

    await message.answer(
        text=unicode_guest_info,
        reply_markup=create_kb_to_payment(
            url=payment.confirmation.confirmation_url,
            payment_id=payment.id,
            subscription_type="👤 Unicode Guest",
            extend=True
        )
    )
    await state.clear()


@router.message(Subscription.extend_subscription, F.text == "🟣 Unicode Base (499 ₽/мес)")
async def extend_subscription_base(message: types.Message, state: FSMContext):
    await message.answer(
        text="🦄",
        reply_markup=reply_builder(["В главное меню"])
    )

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(unicode_base_params, idempotence_key)

    await message.answer(
        text=unicode_base_info,
        reply_markup=create_kb_to_payment(
            url=payment.confirmation.confirmation_url,
            payment_id=payment.id,
            subscription_type="🟣 Unicode Base",
            extend=True
        )
    )
    await state.clear()



@router.message(F.text.lower() == "оформить подписку")
async def get_subscribe(message: types.Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    if is_subscriber:
        await message.answer(
            text="✅ Твоя подписка активна. Пользуйся ей с умом...",
            reply_markup=reply_builder(["В главное меню"])
        )
    else:
        await message.answer(
            text=subscriptions_welcome,
            reply_markup=reply_builder(text=["👤 Unicode Guest (99 ₽/мес)", "🟣 Unicode Base (499 ₽/мес)", "В главное меню"], sizes=[2, 1])
        )


@router.message(F.text == "👤 Unicode Guest (99 ₽/мес)")
async def subscription_unicode_guest(message: types.Message, db: Database) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    if not is_subscriber:
        await message.answer(
            text="🦄",
            reply_markup=reply_builder(["В главное меню"])
        )

        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(unicode_guest_params, idempotence_key)

        await message.answer(
            text=unicode_guest_info,
            reply_markup=create_kb_to_payment(
                url=payment.confirmation.confirmation_url,
                payment_id=payment.id,
                subscription_type="👤 Unicode Guest"
            )
        )

@router.message(F.text == "🟣 Unicode Base (499 ₽/мес)")
async def subscription_unicode_base(message: types.Message, db: Database) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if not is_subscriber:
        await message.answer(
            text="🦄",
            reply_markup=reply_builder(["В главное меню"])
        )

        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(unicode_base_params, idempotence_key)

        await message.answer(
            text=unicode_base_info,
            reply_markup=create_kb_to_payment(
                url=payment.confirmation.confirmation_url,
                payment_id=payment.id,
                subscription_type="🟣 Unicode Base"
            )
        )


@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment(callback: types.CallbackQuery, db: Database, bot: Bot) -> None:
    payment_id = callback.data.split("_")[2]
    payment = Payment.find_one(payment_id)
    # ic(payment.json())
    if payment.status == "succeeded":
        user_info = await db.get_subscriber(user_id=callback.from_user.id)
        is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

        await callback.message.delete()
        await callback.message.answer(
            text="Оплата прошла успешно!",
            reply_markup=reply_builder(["В главное меню"])
        )
        subscriber_info = {
            "tg_id": callback.from_user.id,
            "subscription_type": payment.metadata["subscription_type"],
            "subscription_start": datetime.now(),
            "subscription_end": datetime.now() + timedelta(days=30),
            "payment_method_id": payment.payment_method.id,
            "is_subscribed_to_payments": True
        }

        if not is_subscriber:
            await db.new_subscriber(**subscriber_info)
        else:
            if (payment.metadata["subscription_type"] == user_info.subscription_type):
                subscriber_info["subscription_end"] = user_info.subscription_end + timedelta(days=30)
            await db.subscriber_update(user_id=callback.from_user.id, **subscriber_info)
        await callback.message.answer(
            text="✅ Подписка успешно активирована!\nДобро пожаловать в Unicode 💜!",
            reply_markup=reply_builder(text=["В главное меню"])
        )

        if payment.metadata["subscription_type"] == "unicode_guest":
            formatting_subscription_type = "👤 Unicode Guest (99 ₽/мес)"
        elif payment.metadata["subscription_type"] == "unicode_base":
            formatting_subscription_type = "🟣 Unicode Base (499 ₽/мес)"

        await bot.send_message(
            chat_id=os.getenv("FORWADING_CHAT"),
            text=f"Пользователь @{callback.from_user.username}, `{callback.from_user.full_name}` оформил подписку `{formatting_subscription_type}`",
        )
    elif payment.status == "canceled":
        await callback.message.delete()
        await callback.message.answer(
            text="🚫 Оплата отменена! Вы отменили платеж самостоятельно, истекло время на принятие платежа или платеж был отклонен ЮKassa или платежным провайдером.",
            reply_markup=reply_builder(["В главное меню"])
        )
    elif payment.status == "pending":
        await callback.answer(
            text="⏳ Платеж создан и ожидает действий от пользователя."
        )
    await callback.answer()


@router.message(F.text == "Отменить подписку")
async def unsubscribe(message: types.Message, db: Database, state: FSMContext) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if is_subscriber and user_info.is_subscribed_to_payments:
        await message.answer(
            text=cancel_subscription.format(
                subscription_end=user_info.subscription_end.strftime("%d.%m.%Y %H:%M")
            ),
            reply_markup=reply_builder(["Да", "В главное меню"], sizes=[1, 1])
        )
        await state.set_state(Subscription.confirm_delete)
    else:
        await message.answer(
            text="🚫 В данный момент у тебя нет активной подписки.",
            reply_markup=reply_builder(["В главное меню"])
        )


@router.message(Subscription.confirm_delete, F.text == "Да")
async def confirm_unsubscribe(message: types.Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    await db.subscriber_update(user_id=message.from_user.id, is_subscribed_to_payments=False)
    await message.answer(
        text="✅ Твоя подписка успешно отменена!",
        reply_markup=reply_builder(["В главное меню"])
    )
