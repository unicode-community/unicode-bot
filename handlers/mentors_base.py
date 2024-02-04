import os
from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv
from pyairtable import Api

from db.database import Database
from keyboards.builders import reply_builder
from messages import error_no_subscr_for_mentors_base, link_to_mentors_base, mentors_instructions, mentors_welcome
from utils.states import Mentor

load_dotenv(find_dotenv())
router = Router()

api = Api(os.getenv("AIRTABLE_TOKEN"))
table = api.table(os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_ID"))


@router.message(F.text.lower() == "база менторов")
async def mentors_base(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=mentors_welcome,
        reply_markup=reply_builder(
            text=["Перейти в базу менторов", "Стать ментором", "В главное меню"]
        )
    )

@router.message(F.text.lower() == "стать ментором")
async def become_mentor(message: types.Message, db: Database, state: FSMContext) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    if not is_subscriber:
        await message.answer(
            text=error_no_subscr_for_mentors_base,
            reply_markup=reply_builder(["Оформить подписку", "В главное меню"])
        )
    else:
        is_mentor = await db.get_mentor(tg_id=message.from_user.id)

        if is_mentor:
            await message.answer(
                text="Твоя анкета уже есть в таблице менторов. Что с ней сделать?",
                reply_markup=reply_builder(text=["Изменить", "Удалить", "В главное меню"], sizes=[2, 1])
            )
        else:
            await message.answer(
                text=mentors_instructions,
                reply_markup=reply_builder(text=["Заполнить анкету", "В главное меню"])
            )
        await state.set_state(Mentor.actions)


@router.message(Mentor.actions, F.text == "Удалить")
async def delete_mentor(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        text="Ты уверен что хочешь удалить свою анкету из таблицы менторов?",
        reply_markup=reply_builder(text=["Да", "Смотреть таблицу", "В главное меню"], sizes=[1, 2])
    )
    await state.set_state(Mentor.confirm_delete)


@router.message(Mentor.confirm_delete, F.text == "Да")
async def confirm_delete_mentor(message: types.Message, bot: Bot, db: Database, state: FSMContext) -> None:
    mentor_info = await db.get_mentor(tg_id=message.from_user.id)
    try:
        table.delete(record_id=mentor_info.airtable_record_id)
        await db.delete_mentor(tg_id=message.from_user.id)
        await message.answer(
            text="Ваша анкета успешно удалена!",
            reply_markup=reply_builder(text=["Смотреть таблицу", "В главное меню"])
        )
        await bot.send_message(
            chat_id=os.getenv("FORWADING_CHAT"),
            text=f"Ментор @{message.from_user.username}, {message.from_user.full_name} удалил анкету",
            disable_web_page_preview=True,
            parse_mode=None
        )
    except Exception as e:
        await bot.send_message(
            chat_id=os.getenv("FORWADING_CHAT"),
            text=f"Ошибка при удалении анкеты пользователя @{message.from_user.username}, {message.from_user.full_name}\n\n{e}",
            disable_web_page_preview=True,
            parse_mode=None
        )

    await state.clear()


@router.message(Mentor.actions, F.text == "Изменить")
@router.message(Mentor.actions, F.text == "Заполнить анкету")
async def fill_mentor_form(message: types.Message, db: Database, state: FSMContext) -> None:
    if message.text == "Изменить":
        await state.update_data(action="change")
    else:
        await state.update_data(action="fill")
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(tg_username=message.from_user.username)

    mentor_data_from_db = await db.get_mentor(tg_id=message.from_user.id)
    buttons = ["Оставить текущее", "В главное меню"] if mentor_data_from_db else ["В главное меню"]
    text = "Как тебя зовут?"
    text += f"\n\nСейчас имя в твоей анкете: {mentor_data_from_db.name}" if mentor_data_from_db else ""

    await message.answer(
        text=text,
        reply_markup=reply_builder(text=buttons, sizes=[1, 1])
    )
    await state.set_state(Mentor.name)


@router.message(Mentor.name, F.text)
async def name_mentor(message: types.Message, db: Database, state: FSMContext) -> None:
    mentor_data_from_db = await db.get_mentor(tg_id=message.from_user.id)
    name = mentor_data_from_db.name if message.text == "Оставить текущее" else message.text
    await state.update_data(name=name)
    buttons = ["Оставить текущее", "В главное меню"] if mentor_data_from_db else ["В главное меню"]
    text = "По какой теме ты консультируешь?"
    text += f"\n\nСейчас направление в твоей анкете: {mentor_data_from_db.direction}" if mentor_data_from_db else ""

    await message.answer(
        text=text,
        reply_markup=reply_builder(text=buttons, sizes=[1, 1])
    )
    await state.set_state(Mentor.direction)


@router.message(Mentor.direction, F.text)
async def direction_mentor(message: types.Message, db: Database, state: FSMContext) -> None:
    mentor_data_from_db = await db.get_mentor(tg_id=message.from_user.id)
    direction = mentor_data_from_db.direction if message.text == "Оставить текущее" else message.text
    await state.update_data(direction=direction)

    buttons = ["Оставить текущее", "В главное меню"] if mentor_data_from_db else ["В главное меню"]
    text = "Напиши описание твоей услуги"
    text += f"\n\nСейчас описание в твоей анкете: {mentor_data_from_db.descr}" if mentor_data_from_db else ""

    await message.answer(
        text=text,
        reply_markup=reply_builder(text=buttons, sizes=[1, 1])
    )
    await state.set_state(Mentor.descr)


@router.message(Mentor.descr, F.text)
async def descr_mentor(message: types.Message, db: Database, state: FSMContext) -> None:
    mentor_data_from_db = await db.get_mentor(tg_id=message.from_user.id)
    descr = mentor_data_from_db.descr if message.text == "Оставить текущее" else message.text
    await state.update_data(descr=descr)

    buttons = ["Бесплатно", "Оставить текущее", "В главное меню"] if mentor_data_from_db else ["Бесплатно", "В главное меню"]
    text = "Напиши цену твоей услуги"
    text += f"\n\nСейчас цена в твоей анкете: {mentor_data_from_db.price}" if mentor_data_from_db else ""

    await message.answer(
        text=text,
        reply_markup=reply_builder(text=buttons, sizes=[2, 1])
    )
    await state.set_state(Mentor.price)


@router.message(Mentor.price, F.text)
async def price_mentor(message: types.Message, db: Database, state: FSMContext) -> None:
    mentor_data_from_db = await db.get_mentor(tg_id=message.from_user.id)
    price = mentor_data_from_db.price if message.text == "Оставить текущее" else message.text
    await state.update_data(price=price)

    buttons = ["Оставить текущее", "В главное меню"] if mentor_data_from_db else ["В главное меню"]
    text = "Оставь свои контакты"
    text += f"\n\nСейчас контакты в твоей анкете: {mentor_data_from_db.contact}" if mentor_data_from_db else ""

    await message.answer(
        text=text,
        reply_markup=reply_builder(text=buttons, sizes=[1, 1])
    )

    await state.set_state(Mentor.contact)


@router.message(Mentor.contact, F.text)
async def finish_mentor_form(message: types.Message, bot: Bot, state: FSMContext, db: Database) -> None:
    mentor_data_from_db = await db.get_mentor(tg_id=message.from_user.id)
    contact = mentor_data_from_db.contact if message.text == "Оставить текущее" else message.text
    await state.update_data(contact=contact)

    mentor_form = await state.get_data()

    mentor_record = {
        "Имя": mentor_form["name"],
        "Направление": mentor_form["direction"],
        "Описание": mentor_form["descr"],
        "Цена": mentor_form["price"],
        "Контакт": mentor_form["contact"],
        "tg_id": str(message.from_user.id)
    }

    action = mentor_form.pop("action")
    if action == "change":
        try:
            airtable_record_id, _, _ = table.update(mentor_data_from_db.airtable_record_id, fields=mentor_record).values()
            mentor_form["airtable_record_id"] = airtable_record_id
            await db.mentor_update(user_id=message.from_user.id, **mentor_form)
            await message.answer(
                text="Отлично! Твоя анкета изменена",
                reply_markup=reply_builder(text=["Смотреть таблицу", "В главное меню"])
            )
            await bot.send_message(
                chat_id=os.getenv("FORWADING_CHAT"),
                text=f"@{message.from_user.username}, {message.from_user.full_name} изменил анкету ментора:\n\n" + "\n".join([f"{key}: {value}" for key, value in mentor_record.items() if key != "tg_id"]),
                disable_web_page_preview=True,
                parse_mode=None
            )
        except Exception as e:
            await message.answer(
                text="Произошла ошибка при изменении анкеты",
                reply_markup=reply_builder(text=["В главное меню"])
            )
            await bot.send_message(
                chat_id=os.getenv("FORWADING_CHAT"),
                text=f"Ошибка при изменении анкеты ментора @{message.from_user.username}, {message.from_user.full_name}\n\n{e}",
                disable_web_page_preview=True,
                parse_mode=None
            )
    elif action == "fill":
        try:
            airtable_record_id, _, _ = table.create(mentor_record).values()
            mentor_form["airtable_record_id"] = airtable_record_id
            await db.new_mentor(**mentor_form)
            await message.answer(
                text="Отлично! Твоя анкета добавлена в таблицу",
                reply_markup=reply_builder(text=["Смотреть таблицу", "В главное меню"])
            )
            await bot.send_message(
                chat_id=os.getenv("FORWADING_CHAT"),
                text=f"@{message.from_user.username}, {message.from_user.full_name} создал анкету ментора:\n\n" + "\n".join([f"{key}: {value}" for key, value in mentor_record.items() if key != "tg_id"]),
                disable_web_page_preview=True,
                parse_mode=None
            )

        except Exception as e:
            await message.answer(
                text="Произошла ошибка при создании анкеты",
                reply_markup=reply_builder(text=["В главное меню"])
            )
            await bot.send_message(
                chat_id=os.getenv("FORWADING_CHAT"),
                text=f"Ошибка при создании анкеты ментора @{message.from_user.username}, {message.from_user.full_name}\n\n{e}",
                disable_web_page_preview=True,
                parse_mode=None
            )

    await state.clear()


@router.message(F.text.lower() == "смотреть таблицу")
@router.message(F.text.lower() == "перейти в базу менторов")
async def redirect_mentors_base(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=link_to_mentors_base,
        reply_markup=reply_builder(text=["В главное меню"]),
        disable_web_page_preview=True
    )
