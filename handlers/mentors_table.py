import os
import uuid

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv
from pyairtable import Api
from yookassa import Payment

from db.database import Database
from keyboards.general import return_to_menu
from keyboards.mentors_table import (
    confirm_delete_and_return_to_menu,
    create_approve_or_reject_mentor_form,
    create_delete_mentor,
    create_redirect_to_mentors_table_and_subscribe_and_return_to_menu,
    edit_and_delete_mentor_form_and_return_to_menu,
    fill_mentor_form_and_return_to_menu,
    free_price_and_return_to_menu,
    redirect_to_mentors_table_and_become_mentor_and_return_to_menu,
)
from messages.general import not_text_message
from messages.mentors_table import (
    ask_mentor_area,
    ask_mentor_contact,
    ask_mentor_descr,
    ask_mentor_name,
    ask_mentor_price,
    become_mentor_instructions,
    confirm_delete_mentor,
    mentor_in_table,
    successful_delete,
    successful_fill_mentor,
    welcome_mentors_table,
)
from utils import get_subscription_status
from utils.payments import create_subscription_params
from utils.states import Mentor

load_dotenv(find_dotenv())
router = Router()

api = Api(os.getenv("AIRTABLE_TOKEN"))
table = api.table(os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_ID"))


@router.callback_query(F.data == "unicode_mentors_table")
async def mentors_base(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()

    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if subscriber_info["is_subscriber"]:
        kb = redirect_to_mentors_table_and_become_mentor_and_return_to_menu
    else:
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(create_subscription_params(price=499), idempotency_key=idempotence_key)
        kb = create_redirect_to_mentors_table_and_subscribe_and_return_to_menu(url=payment.confirmation.confirmation_url, payment_id=payment.id)

    await callback.message.answer(
        text=welcome_mentors_table,
        reply_markup=kb
    )

    await callback.answer()


@router.callback_query(F.data == "become_mentor")
async def become_mentor(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    is_mentor = await db.get_mentor(tg_id=callback.from_user.id)

    if is_mentor:
        await callback.message.answer(
            text=mentor_in_table,
            reply_markup=edit_and_delete_mentor_form_and_return_to_menu
        )
    else:
        await callback.message.answer(
            text=become_mentor_instructions,
            reply_markup=fill_mentor_form_and_return_to_menu
        )
    await state.set_state(Mentor.actions)
    await callback.answer()


@router.callback_query(Mentor.actions, F.data == "fill_mentor_form")
async def fill_mentor_form(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        text=ask_mentor_name,
        reply_markup=return_to_menu
    )
    await state.set_state(Mentor.name)
    await callback.answer()


@router.message(Mentor.name, F.text)
async def fill_mentor_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)

    await message.answer(
        text=ask_mentor_area,
        reply_markup=return_to_menu
    )

    await state.set_state(Mentor.area)


@router.message(Mentor.area, F.text)
async def fill_mentor_area(message: types.Message, state: FSMContext) -> None:
    await state.update_data(direction=message.text)

    await message.answer(
        text=ask_mentor_descr,
        reply_markup=return_to_menu
    )

    await state.set_state(Mentor.descr)


@router.message(Mentor.descr, F.text)
async def fill_mentor_descr(message: types.Message, state: FSMContext) -> None:
    await state.update_data(descr=message.text)

    await message.answer(
        text=ask_mentor_price,
        reply_markup=free_price_and_return_to_menu
    )

    await state.set_state(Mentor.price)


@router.callback_query(Mentor.price, F.data == "free_price")
async def fill_mentor_free_price(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.update_data(price="Бесплатно")

    await callback.message.answer(
        text=ask_mentor_contact,
        reply_markup=return_to_menu
    )

    await callback.answer()
    await state.set_state(Mentor.contact)


@router.message(Mentor.price, F.text)
async def fill_mentor_price(message: types.Message, state: FSMContext) -> None:
    await state.update_data(price=message.text)

    await message.answer(
        text=ask_mentor_contact,
        reply_markup=return_to_menu
    )
    await state.set_state(Mentor.contact)


@router.message(Mentor.contact, F.text)
async def fill_mentor_contact(message: types.Message, state: FSMContext, bot: Bot, db: Database) -> None:
    await state.update_data(contact=message.text)

    await message.answer(
        text=successful_fill_mentor,
        reply_markup=return_to_menu
    )

    mentor_form = await state.get_data()

    mentor_form["tg_id"] = message.from_user.id

    await db.new_mentor(**mentor_form)

    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"@{message.from_user.username}, `{message.from_user.full_name}` заполнил анкету ментора:\n\n"
        f"*0️⃣ tg_id*: `{message.from_user.id}`\n"
        f"*1️⃣ Имя:* `{mentor_form['name']}`\n"
        f"*2️⃣ Направление:* `{mentor_form['direction']}`\n"
        f"*3️⃣ Описание:* ```\n{mentor_form['descr']}```\n"
        f"*4️⃣ Цена:* `{mentor_form['price']}`\n"
        f"*5️⃣ Контакт:* `{mentor_form['contact']}`",
        disable_web_page_preview=True,
        reply_markup=create_approve_or_reject_mentor_form(tg_id=message.from_user.id),
        parse_mode="Markdown"
    )

    await state.clear()


@router.callback_query(Mentor.actions, F.data == "delete_mentor_form")
async def delete_mentor_form(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        text=confirm_delete_mentor,
        reply_markup=confirm_delete_and_return_to_menu
    )
    await state.set_state(Mentor.confirm_delete)
    await callback.answer()


@router.callback_query(Mentor.confirm_delete, F.data == "confirm_delete_mentor_form")
async def confirm_delete_mentor_form(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    mentor_info = await db.get_mentor(tg_id=callback.from_user.id)

    if mentor_info.airtable_record_id:
        table.delete(record_id=mentor_info.airtable_record_id)

    await db.delete_mentor(tg_id=callback.from_user.id)
    await callback.message.answer(
        text=successful_delete,
        reply_markup=return_to_menu
    )
    await state.clear()
    await callback.answer()


@router.message(Mentor.name, ~F.text)
@router.message(Mentor.price, ~F.text)
@router.message(Mentor.descr, ~F.text)
@router.message(Mentor.contact, ~F.text)
@router.message(Mentor.area, ~F.text)
async def incorrect_text(message: types.Message) -> None:
    await message.answer(
        text=not_text_message,
        reply_markup=return_to_menu
    )


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
        "tg_id": tg_id
    }

    if mentor_info.airtable_record_id:
        airtable_record_id, _, _ = table.update(record_id=mentor_info.airtable_record_id, fields=mentor_record).values()
    else:
        airtable_record_id, _, _ = table.create(fields=mentor_record).values()

    await db.mentor_update(tg_id=tg_id, airtable_record_id=airtable_record_id)

    await callback.message.edit_reply_markup(
        reply_markup=create_delete_mentor(tg_id=tg_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reject_mentor"))
async def reject_mentor_form(callback: types.CallbackQuery, db: Database) -> None:
    tg_id = int(callback.data.split("_")[-1])

    await db.delete_mentor(tg_id=tg_id)

    await callback.message.edit_reply_markup(
        reply_markup=create_delete_mentor(tg_id=tg_id)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("delete_mentor"))
async def delete_mentor(callback: types.CallbackQuery, db: Database) -> None:
    tg_id = int(callback.data.split("_")[-1])

    mentor_info = await db.get_mentor(tg_id=tg_id)

    await db.delete_mentor(tg_id=tg_id)
    table.delete(record_id=mentor_info.airtable_record_id)

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.answer()
