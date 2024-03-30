from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from icecream import ic

import keyboards.admin as keyboards
from db.database import Database
from filters.filters import IsAdmin
from keyboards.general import return_to_menu
from utils.states import Admin

router = Router()
router.message.filter(IsAdmin())


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    await message.answer(
        text="Что хочешь сделать?",
        reply_markup=keyboards.admin_functions
    )

@router.callback_query(F.data == "admin_send_messages")
async def admin_send_messages(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Выбери какому сегменту пользователей отправить сообщение",
        reply_markup=keyboards.send_messages_segments
    )
    await callback.answer()
    await state.set_state(Admin.segment)


@router.callback_query(Admin.segment)
async def get_segment(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(segment=callback.data.split("_", maxsplit=1)[1])
    await callback.message.answer(
        text="Напиши сообщение, которое хочешь отправить",
        reply_markup=return_to_menu
    )
    await callback.answer()
    await state.set_state(Admin.message)


@router.message(Admin.message)
async def send_message(message: types.Message, state: FSMContext, db: Database):
    segment = await state.get_data()

    if segment["segment"] == "all_users":
        users = await db.get_all_users()
    elif segment["segment"] == "all_subscribers":
        users = await db.get_all_subscribers()
    elif segment["segment"] == "mentors":
        users = await db.get_all_mentors()
    elif segment["segment"] == "unicode_guest":
        users = await db.get_all_subscribers(subscription_db_name="unicode_guest")
    elif segment["segment"] == "unicode_starter":
        users = await db.get_all_subscribers(subscription_db_name="unicode_starter")
    elif segment["segment"] == "unicode_base":
        users = await db.get_all_subscribers(subscription_db_name="unicode_base")
    else:
        users = []

    count_success = 0
    count_fail = 0
    for user in users:
        try:
            await message.send_copy(chat_id=user.tg_id)
            count_success += 1
        except Exception as err:
            count_fail += 1
            ic(err)

    await message.answer(
        text=f"Успешно отправлено `{count_success}` пользователям, не удалось отправить `{count_fail}`",
        reply_markup=return_to_menu
    )
    await state.set_state(Admin.segment)


@router.callback_query(F.data == "admin_remove_subscription")
@router.callback_query(F.data == "admin_give_subscription")
async def admin_give_or_remove_subscription(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Напиши юзернейм пользователя",
        reply_markup=return_to_menu
    )

    await state.set_state(Admin.find_user)
    await callback.answer()


@router.message(Admin.find_user, F.text)
async def admin_find_user(message: types.Message, db: Database):
    if message.text.startswith("@"):
        username = message.text[1:]
    else:
        username = message.text

    user_info = await db.get_user_by_username(tg_username=username)

    if user_info:
        await message.answer(
            text=f"Пользователь найден."
            f"\nЕсли хочешь выдать подписку, то выбери тип подписки. Она будет действовать 30 дней, начиная с этого момента"
            f"\nЕсли хочешь удалить подписку у пользователя, то подписка будет прервана с текущего момента" # TODO спросить как лучше сделать
            f"\n\nИнформация о пользователе:"
            f"\n0️⃣ *tg_id*: `{user_info.tg_id}`"
            f"\n1️⃣ *Тип подписки*: `{user_info.subscription_db_name}`"
            f"\n2️⃣ *Дата начала подписки*: `{user_info.subscription_start}`"
            f"\n3️⃣ *Дата окончания подписки*: `{user_info.subscription_end}`"
            f"\n4️⃣ *Подписан на регулярные платежи*: `{user_info.is_subscribed_to_payments}`",
            reply_markup=keyboards.give_or_delete_subscription(tg_id=user_info.tg_id),
        )
    else:
        await message.answer(
            text="Пользователь не найден",
            reply_markup=return_to_menu
        )


@router.callback_query(F.data.startswith("give_unicode_"))
async def give_subscription(callback: types.CallbackQuery, state: FSMContext, db: Database):
    await state.clear()

    subscr_type = "_".join(callback.data.split("_")[1:3])
    tg_id = int(callback.data.split("_")[-1])

    subscr_info = {
        "subscription_db_name": subscr_type,
        "subscription_start": datetime.now(),
        "subscription_end": datetime.now() + timedelta(days=30)
    }

    await db.user_update(user_id=tg_id, **subscr_info)

    await callback.message.answer(
        text="Подписка выдана",
        reply_markup=return_to_menu
    )
    await callback.answer()


@router.callback_query(F.data.startswith("remove_subscription_"))
async def remove_subscription(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.answer(
        text="Подтвердить удаление подписки",
        reply_markup=keyboards.confirm_remove_subscription(tg_id=callback.data.split("_")[-1])
    )

    await callback.answer()


@router.callback_query(F.data.startswith("confirm_remove_subscription_"))
async def confirm_remove_subscription(callback: types.CallbackQuery, state: FSMContext, db: Database):
    await state.clear()

    tg_id = int(callback.data.split("_")[-1])

    subscr_info = {
        "subscription_db_name": None,
        "subscription_start": None,
        "subscription_end": None,
        "is_subscribed_to_payments": False
    }

    await db.user_update(user_id=tg_id, **subscr_info)

    await callback.message.answer(
        text="Подписка удалена",
        reply_markup=return_to_menu
    )
    await callback.answer()
