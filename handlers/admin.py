from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from icecream import ic
from pytz import timezone

import keyboards.admin as kb
import messages.admin as msg
from db import Database
from filters import IsAdmin
from keyboards import return_to_menu
from utils import Admin, get_subscription_status

router = Router()
router.message.filter(IsAdmin())


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    await message.answer(text="Что хочешь сделать?", reply_markup=kb.admin_functions)


@router.callback_query(F.data == "admin_send_messages")
async def admin_send_messages(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Выбери какому сегменту пользователей отправить сообщение", reply_markup=kb.send_messages_segments
    )
    await callback.answer()
    await state.set_state(Admin.segment)


@router.callback_query(Admin.segment)
async def get_segment(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(segment=callback.data.split("_", maxsplit=1)[1])
    await callback.message.answer(text="Введи сообщение для рассылки", reply_markup=return_to_menu)
    await callback.answer()
    await state.set_state(Admin.message)


@router.message(Admin.message)
async def send_message(message: types.Message, state: FSMContext, db: Database):
    segment = await state.get_data()

    if segment["segment"] == "subscribers":
        users = await db.get_all_subscribers()
    elif segment["segment"] == "mentors":
        users = await db.get_all_mentors()
    elif segment["segment"] == "others":
        users = await db.get_all_unsubscribers()
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
        reply_markup=return_to_menu,
    )
    await state.set_state(Admin.segment)


@router.callback_query(F.data == "admin_remove_subscription")
@router.callback_query(F.data == "admin_give_subscription")
async def admin_give_or_remove_subscription(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Введи @username пользователя кому выдать (отобрать) подписку", reply_markup=return_to_menu
    )

    await state.set_state(Admin.find_user)
    await callback.answer()


@router.message(Admin.find_user, F.text)
async def admin_find_user(message: types.Message, db: Database):
    username = message.text[1:] if message.text.startswith("@") else message.text

    user_id = await db.get_user_id_by_username(tg_username=username)

    user_info = await get_subscription_status(user_tg_id=user_id, db=db)

    if user_info["is_bot_user"]:
        await message.answer(
            text=msg.user_description.format(
                tg_id=user_id,
                is_subscriber=user_info["is_subscriber"],
                subscription_start=user_info["subscription_start"],
                subscription_end=user_info["subscription_end"].strftime("%d.%m.%Y %H:%M"),
                is_subscribed_to_payments=user_info["is_subscribed_to_payments"],
            ),
            reply_markup=kb.give_or_delete_subscription(tg_id=user_id),
        )
    else:
        await message.answer(text="Пользователь не найден", reply_markup=return_to_menu)


@router.callback_query(F.data.startswith("give_subscription_"))
async def give_subscription(callback: types.CallbackQuery, state: FSMContext, db: Database):
    await state.clear()

    tg_id = int(callback.data.split("_")[-1])

    subscr_info = {
        "is_subscriber": True,
        "subscription_start": datetime.now(tz=timezone("Europe/Moscow")),
        "subscription_end": datetime.now(tz=timezone("Europe/Moscow")) + timedelta(days=30),
        "is_subscribed_to_payments": False,
    }

    try:
        await db.user_update(user_id=tg_id, **subscr_info)

        await callback.message.answer(text="✅ Подписка успешно добавлена.", reply_markup=return_to_menu)
    except Exception as err:
        await callback.message.answer(text="❌ Возникла ошибка, подписка не добавлена.", reply_markup=return_to_menu)

        ic(err)
    await callback.answer()


@router.callback_query(F.data.startswith("remove_subscription_"))
async def remove_subscription(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.answer(
        text="Подтвердить удаление подписки",
        reply_markup=kb.confirm_remove_subscription(tg_id=callback.data.split("_")[-1]),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("confirm_remove_subscription_"))
async def confirm_remove_subscription(callback: types.CallbackQuery, state: FSMContext, db: Database):
    await state.clear()

    tg_id = int(callback.data.split("_")[-1])

    subscr_info = {
        "is_subscriber": None,
        "subscription_start": None,
        "subscription_end": None,
        "is_subscribed_to_payments": False,
    }

    await db.user_update(user_id=tg_id, **subscr_info)

    await callback.message.answer(text="Подписка удалена", reply_markup=return_to_menu)
    await callback.answer()
