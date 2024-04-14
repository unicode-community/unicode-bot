import os
import uuid

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from pyairtable import Api
from yookassa import Payment

import keyboards.mentors_table as kb
import messages.mentors_table as msg
from config import Config
from db import Database
from keyboards import return_to_menu
from messages import not_text_message
from utils import Mentor, create_subscription_params, get_subscription_status

router = Router()

api = Api(os.getenv("AIRTABLE_TOKEN"))
table = api.table(os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_ID"))


@router.callback_query(F.data == "unicode_mentors_table")
async def mentors_base(callback: types.CallbackQuery, state: FSMContext, db: Database, cfg: Config) -> None:
    await state.clear()

    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if subscriber_info["is_subscriber"]:
        main_mentor_kb = kb.redirect_to_mentors_table_and_become_mentor_and_return_to_menu
    else:
        payment = Payment.create(
            create_subscription_params(price=cfg.subscription_price, user_id=callback.from_user.id),
            idempotency_key=str(uuid.uuid4()),
        )
        main_mentor_kb = kb.create_redirect_to_mentors_table_and_subscribe_and_return_to_menu(
            url=payment.confirmation.confirmation_url, payment_id=payment.id
        )

    await callback.message.answer(text=msg.welcome_mentors_table, reply_markup=main_mentor_kb)

    await callback.answer()


@router.callback_query(F.data == "become_mentor")
async def become_mentor(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    is_mentor = await db.get_mentor(tg_id=callback.from_user.id)

    if is_mentor:
        await callback.message.answer(
            text=msg.mentor_in_table, reply_markup=kb.edit_and_delete_mentor_form_and_return_to_menu
        )
    else:
        await callback.message.answer(
            text=msg.become_mentor_instructions, reply_markup=kb.fill_mentor_form_and_return_to_menu
        )
    await state.set_state(Mentor.actions)
    await callback.answer()


@router.callback_query(Mentor.actions, F.data == "fill_mentor_form")
async def fill_mentor_form(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=msg.ask_mentor_name, reply_markup=return_to_menu)
    await state.set_state(Mentor.name)
    await callback.answer()


@router.message(Mentor.name, F.text)
async def fill_mentor_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)

    await message.answer(text=msg.ask_mentor_area, reply_markup=return_to_menu)

    await state.set_state(Mentor.area)


@router.message(Mentor.area, F.text)
async def fill_mentor_area(message: types.Message, state: FSMContext) -> None:
    await state.update_data(direction=message.text)

    await message.answer(text=msg.ask_mentor_descr, reply_markup=return_to_menu)

    await state.set_state(Mentor.descr)


@router.message(Mentor.descr, F.text)
async def fill_mentor_descr(message: types.Message, state: FSMContext) -> None:
    await state.update_data(descr=message.text)

    await message.answer(text=msg.ask_mentor_price, reply_markup=kb.free_price_and_return_to_menu)

    await state.set_state(Mentor.price)


@router.callback_query(Mentor.price, F.data == "free_price")
async def fill_mentor_free_price(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.update_data(price="Бесплатно")

    await callback.message.answer(text=msg.ask_mentor_contact, reply_markup=return_to_menu)

    await callback.answer()
    await state.set_state(Mentor.contact)


@router.message(Mentor.price, F.text)
async def fill_mentor_price(message: types.Message, state: FSMContext) -> None:
    await state.update_data(price=message.text)

    await message.answer(text=msg.ask_mentor_contact, reply_markup=return_to_menu)
    await state.set_state(Mentor.contact)


@router.message(Mentor.contact, F.text)
async def fill_mentor_contact(message: types.Message, state: FSMContext, bot: Bot, db: Database) -> None:
    await state.update_data(contact=message.text)

    await message.answer(text=msg.successful_fill_mentor, reply_markup=return_to_menu)

    mentor_form = await state.get_data()

    mentor_form["tg_id"] = message.from_user.id

    await db.new_mentor(**mentor_form)

    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=msg.message_for_admins.format(
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            tg_id=message.from_user.id,
            name=mentor_form["name"],
            direction=mentor_form["direction"],
            descr=mentor_form["descr"],
            price=mentor_form["price"],
            contact=mentor_form["contact"],
        ),
        disable_web_page_preview=True,
        reply_markup=kb.create_approve_or_reject_mentor_form(tg_id=message.from_user.id),
        parse_mode="Markdown",
    )

    await state.clear()


@router.callback_query(Mentor.actions, F.data == "delete_mentor_form")
async def delete_mentor_form(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=msg.confirm_delete_mentor, reply_markup=kb.confirm_delete_and_return_to_menu)
    await state.set_state(Mentor.confirm_delete)
    await callback.answer()


@router.callback_query(Mentor.confirm_delete, F.data == "confirm_delete_mentor_form")
async def confirm_delete_mentor_form(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    mentor_info = await db.get_mentor(tg_id=callback.from_user.id)

    if mentor_info.airtable_record_id:
        table.delete(record_id=mentor_info.airtable_record_id)

    await db.delete_mentor(tg_id=callback.from_user.id)
    await callback.message.answer(text=msg.successful_delete, reply_markup=return_to_menu)
    await state.clear()
    await callback.answer()


@router.message(Mentor.name, ~F.text)
@router.message(Mentor.price, ~F.text)
@router.message(Mentor.descr, ~F.text)
@router.message(Mentor.contact, ~F.text)
@router.message(Mentor.area, ~F.text)
async def incorrect_text(message: types.Message) -> None:
    await message.answer(text=not_text_message, reply_markup=return_to_menu)


@router.callback_query(F.data.startswith("approve_mentor"))
async def approve_mentor_form(callback: types.CallbackQuery, db: Database) -> None:
    tg_id = int(callback.data.split("_")[-1])

    mentor_info = await db.get_mentor(tg_id=tg_id)

    mentor_record = {
        "Имя": mentor_info.name,
        "Направление": mentor_info.direction,
        "Описание": mentor_info.descr,
        "Цена": mentor_info.price,
        "Контакт": mentor_info.contact,
        "tg_id": tg_id,
    }

    if mentor_info.airtable_record_id:
        airtable_record_id, _, _ = table.update(record_id=mentor_info.airtable_record_id, fields=mentor_record).values()
    else:
        airtable_record_id, _, _ = table.create(fields=mentor_record).values()

    await db.mentor_update(tg_id=tg_id, airtable_record_id=airtable_record_id)

    await callback.message.edit_reply_markup(reply_markup=kb.create_delete_mentor(tg_id=tg_id))
    await callback.answer()


@router.callback_query(F.data.startswith("reject_mentor"))
async def reject_mentor_form(callback: types.CallbackQuery, db: Database) -> None:
    tg_id = int(callback.data.split("_")[-1])

    await db.delete_mentor(tg_id=tg_id)

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer()


@router.callback_query(F.data.startswith("delete_mentor"))
async def delete_mentor(callback: types.CallbackQuery, db: Database) -> None:
    tg_id = int(callback.data.split("_")[-1])

    mentor_info = await db.get_mentor(tg_id=tg_id)

    await db.delete_mentor(tg_id=tg_id)
    table.delete(record_id=mentor_info.airtable_record_id)

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer()
