import os
from datetime import datetime, timedelta

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, PreCheckoutQuery
from dotenv import find_dotenv, load_dotenv

from db.database import Database
from keyboards.builders import reply_builder
from utils.states import Subscription

router = Router()
load_dotenv(find_dotenv())

@router.message(F.text.lower() == "подписка")
async def subscribe(message: types.Message, db: Database, state: FSMContext):
    await state.clear()
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if is_subscriber:
        await message.answer(
            text=f"Тип твоей подписки: `{user_info.subscription_type}`\n"
            f"Подписка действительна до: `{user_info.subscription_end.strftime('%d.%m.%Y %H:%M')}`",
            reply_markup=reply_builder(["Оформить подписку", "Отменить подписку", "В главное меню"], sizes=[2, 1])
        )
    else:
        await message.answer(
            text="В данный момент у тебя нет активной подписки.",
            reply_markup=reply_builder(["Оформить подписку", "В главное меню"], sizes=[1, 1])
        )

@router.message(F.text.lower() == "оформить подписку")
async def get_subscribe(message: types.Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    if is_subscriber:
        await message.answer(
            text="Твоя подписка активна. Пользуйся ей с умом...",
            reply_markup=reply_builder(["В главное меню"])
        )
    else:
        await message.answer(
            text="Пожалуйста, выбери тип подписки, который тебя интересует",
            reply_markup=reply_builder(text=["Unicode Base (499 ₽/мес)", "В главное меню"], sizes=[1, 1])
        )


@router.message(F.text.lower() == "отменить подписку")
async def unsubscribe(message: types.Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    if not is_subscriber:
        await message.answer(
            text="В данный момент у тебя нет активной подписки.",
            reply_markup=reply_builder(["В главное меню"])
        )
    else:
        # await db.unsubscribe_user(tg_id=message.from_user.id)
        await message.answer(
            text="Ты уверен, что хочешь отменить свою подписку?",
            reply_markup=reply_builder(["Да", "В главное меню"], sizes=[1, 1])
        )
        await state.set_state(Subscription.confirm_delete)


@router.message(Subscription.confirm_delete, F.text == "Да")
async def confirm_unsubscribe(message: types.Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    await db.unsubscribe_user(tg_id=message.from_user.id)
    await message.answer(
        text="Твоя подписка успешно отменена!",
        reply_markup=reply_builder(["В главное меню"])
    )


@router.message(F.text == "Unicode Base (499 ₽/мес)")
async def base_subscription(message: types.Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()

    await bot.send_invoice(
        chat_id=message.from_user.id,
        title="ТУТ ЗАГОЛОВОК",
        description="ТУТ ОПИСАНИЕ",
        provider_token=os.getenv("YOOKASSA_TOKEN"),
        currency="rub",
        prices=[LabeledPrice(label="Unicode Base", amount=499 * 100)],
        start_parameter="unicode_bot",
        request_timeout=60,
        payload="buy unicode base",
        photo_url="https://s7.ezgif.com/tmp/ezgif-7-f8be84ad0a.jpg",
        photo_height=500,
        photo_width=500
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )

    print(pre_checkout_query)

@router.message(F.successful_payment)
async def successful_payment(message: types.Message, bot: Bot, db: Database):
    subscriber_info = {
        "tg_id": message.from_user.id,
        "subscription_type": "Unicode Base (499 ₽/мес)",
        "subscription_start": datetime.now(),
        "subscription_end": datetime.now() + timedelta(days=30)
    }
    await db.new_subscriber(**subscriber_info)
    await message.answer(
        text="Оплата прошла успешно! Добро пожаловать в Unicode 💜!",
        reply_markup=reply_builder(text=["В главное меню"])
    )
    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"Пользователь @{message.from_user.username}, `{message.from_user.full_name}` оформил подписку `Unicode Base (499 ₽/мес)`",
    )
