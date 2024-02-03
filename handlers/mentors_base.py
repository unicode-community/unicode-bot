import os
from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv

from db.database import Database
from keyboards.builders import reply_builder
from messages import error_no_subscr_for_mentors_base, link_to_mentors_base, mentors_instructions, mentors_welcome
from utils.states import Mentor

load_dotenv(find_dotenv())
router = Router()

@router.message(F.text.lower() == "база менторов")
async def mentors_base(message: types.Message) -> None:
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


@router.message(Mentor.actions, F.text == "Изменить")
async def edit_mentor(message: types.Message, db: Database) -> None:
    mentor_form = await db.get_mentor(tg_id=message.from_user.id)
    await message.answer(
        text=f"Твоя анкета выглядит так:\n\nИмя: {mentor_form.name}\nНаправление: {mentor_form.direction}\nОписание: {mentor_form.descr}\nЦена: {mentor_form.price}\nКонтакт: {mentor_form.contact}",
        reply_markup=reply_builder(text=["В главное меню"])
    )


@router.message(Mentor.confirm_delete, F.text == "Да")
async def confirm_delete_mentor(message: types.Message, db: Database, state: FSMContext) -> None:
    await db.delete_mentor(tg_id=message.from_user.id)
    await message.answer(
        text="Ваша анкета успешно удалена!",
        reply_markup=reply_builder(text=["Смотреть таблицу", "В главное меню"])
    )
    await state.clear()


@router.message(Mentor.actions, F.text == "Заполнить анкету")
async def fill_mentor_form(message: types.Message, state: FSMContext) -> None:
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(tg_username=message.from_user.username)

    await message.answer(
        text="Как тебя зовут?",
        reply_markup=reply_builder(["В главное меню"])
    )
    await state.set_state(Mentor.name)


@router.message(Mentor.name, F.text)
async def name_mentor(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(
        text="По какой теме ты консультируешь?",
        reply_markup=reply_builder(["В главное меню"])
    )
    await state.set_state(Mentor.direction)


@router.message(Mentor.direction, F.text)
async def direction_mentor(message: types.Message, state: FSMContext) -> None:
    await state.update_data(direction=message.text)
    await message.answer(
        text="Напиши описание твоей услуги",
        reply_markup=reply_builder(text=["В главное меню"])
    )
    await state.set_state(Mentor.descr)


@router.message(Mentor.descr, F.text)
async def descr_mentor(message: types.Message, state: FSMContext) -> None:
    await state.update_data(descr=message.text)
    await message.answer(
        text="Напиши цену твоей услуги",
        reply_markup=reply_builder(text=["Бесплатно", "В главное меню"], sizes=[1, 1])
    )
    await state.set_state(Mentor.price)


@router.message(Mentor.price, F.text)
async def price_mentor(message: types.Message, state: FSMContext) -> None:
    await state.update_data(price=message.text)
    await message.answer(
        text="Оставь свои контакты",
        reply_markup=reply_builder(text=["В главное меню"])
    )
    await state.set_state(Mentor.contact)


@router.message(Mentor.contact, F.text)
async def finish_mentor_form(message: types.Message, bot: Bot, state: FSMContext, db: Database) -> None:
    await state.update_data(contact=message.text)

    # TODO добавление в airtable

    mentor_form = await state.get_data()
    await db.new_mentor(**mentor_form)

    await message.answer(
        text="Отлично! Твоя анкета добавлена в таблицу",
        reply_markup=reply_builder(text=["Смотреть таблицу", "В главное меню"])
    )

    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"Пользователь @{message.from_user.username}, {message.from_user.full_name} создал анкету ментора:\n\nИмя: {mentor_form['name']}\nНаправление: {mentor_form['direction']}\nОписание: {mentor_form['descr']}\nЦена: {mentor_form['price']}\nКонтакт: {mentor_form['contact']}",
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
