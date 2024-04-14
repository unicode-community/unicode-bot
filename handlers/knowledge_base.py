import uuid

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from yookassa import Payment

import keyboards.knowledge_base as kb
import messages.knowledge_base as msg
from config import Config
from db import Database
from keyboards import create_kb_to_payment, return_to_menu
from messages import not_text_message
from utils import Interview, Material, Other, Question, create_subscription_params, get_subscription_status

router = Router()


@router.callback_query(F.data == "unicode_knowledge_base")
async def knowledge_base(callback: types.CallbackQuery, state: FSMContext, db: Database, cfg: Config) -> None:
    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    if subscriber_info["is_subscriber"]:
        await callback.message.answer(
            text=msg.welcome_knowledge_base,
            reply_markup=kb.redirect_knowledge_base_and_update_base_and_return_to_menu,
        )
    else:
        payment = Payment.create(
            create_subscription_params(
                price=cfg.subscription_price, return_url=cfg.bot_link, user_id=callback.from_user.id
            ),
            idempotency_key=str(uuid.uuid4()),
        )
        await callback.message.answer(
            text=msg.welcome_knowledge_base + "\n" + msg.add_for_unsubscribers,
            reply_markup=create_kb_to_payment(url=payment.confirmation.confirmation_url, payment_id=payment.id),
        )

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "update_knowledge_base")
async def update_knowledge_base(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(text=msg.ask_which_to_send, reply_markup=kb.information_options)
    await callback.answer()


@router.callback_query(F.data == "add_questions")
async def add_questions(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=msg.ask_interview_position, reply_markup=return_to_menu)
    await callback.answer()
    await state.set_state(Question.position)


@router.message(Question.position, F.text)
async def add_questions_position(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer(text=msg.ask_interview_questions, reply_markup=return_to_menu)
    await state.set_state(Question.info)


@router.message(Question.info, F.text)
async def add_questions_info(message: types.Message, state: FSMContext, bot: Bot, cfg: Config) -> None:
    await state.update_data(info=message.text)
    await message.answer(text=msg.feedback_after_interview, reply_markup=return_to_menu)

    data = await state.get_data()

    await bot.send_message(
        chat_id=cfg.forwarding_chat,
        text=f"@{message.from_user.username}, `{message.from_user.full_name}`\n\n"
        f"*1️⃣ Топик:* `Вопросы с собеседования`\n"
        f"*2️⃣ Позиция:* `{data['position']}`\n"
        f"*3️⃣ Вопросы:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
    )
    await state.clear()


@router.callback_query(F.data == "add_materials")
async def add_materials(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=msg.ask_materials_descr, reply_markup=return_to_menu)
    await callback.answer()
    await state.set_state(Material.descr)


@router.message(Material.descr, F.text)
async def add_materials_descr(message: types.Message, state: FSMContext) -> None:
    await state.update_data(descr=message.text)
    await message.answer(text=msg.ask_materials_info, reply_markup=return_to_menu)
    await state.set_state(Material.info)


@router.message(Material.info, F.text)
async def add_materials_info(message: types.Message, state: FSMContext, bot: Bot, cfg: Config) -> None:
    await state.update_data(info=message.text)

    await message.answer(text=msg.feedback_after_materials, reply_markup=return_to_menu)

    data = await state.get_data()

    await bot.send_message(
        chat_id=cfg.forwarding_chat,
        text=f"@{message.from_user.username}, `{message.from_user.full_name}`\n\n"
        f"*1️⃣ Топик:* `Полезные материалы`\n"
        f"*2️⃣ Описание:*\n```\n{data['descr']}```\n"
        f"*3️⃣ Информация:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
    )
    await state.clear()


@router.callback_query(F.data == "add_summary")
async def add_summary(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=msg.ask_summary_position, reply_markup=return_to_menu)
    await callback.answer()
    await state.set_state(Interview.position)


@router.message(Interview.position, F.text)
async def add_summary_position(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer(text=msg.ask_summary_company, reply_markup=return_to_menu)
    await state.set_state(Interview.company)


@router.message(Interview.company, F.text)
async def add_summary_company(message: types.Message, state: FSMContext) -> None:
    await state.update_data(company=message.text)
    await message.answer(text=msg.ask_summary, reply_markup=return_to_menu)
    await state.set_state(Interview.info)


@router.message(Interview.info, F.text)
async def add_summary_info(message: types.Message, state: FSMContext, bot: Bot, cfg: Config) -> None:
    await state.update_data(info=message.text)

    await message.answer(text=msg.feedback_after_summary, reply_markup=return_to_menu)

    data = await state.get_data()

    await bot.send_message(
        chat_id=cfg.forwarding_chat,
        text=f"@{message.from_user.username}, `{message.from_user.full_name}`\n\n"
        f"*1️⃣ Топик:* `Резюме собеса`\n"
        f"*2️⃣ Позиция:* `{data['position']}`\n"
        f"*3️⃣ Компания:* `{data['company']}`\n"
        f"*4️⃣ Информация:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
    )
    await state.clear()


@router.callback_query(F.data == "add_other")
async def add_other(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=msg.ask_other_info, reply_markup=return_to_menu)
    await callback.answer()
    await state.set_state(Other.info)


@router.message(Other.info, F.text)
async def add_other_info(message: types.Message, state: FSMContext, bot: Bot, cfg: Config) -> None:
    await state.update_data(info=message.text)

    await message.answer(text=msg.feedback_after_other, reply_markup=return_to_menu)

    data = await state.get_data()

    await bot.send_message(
        chat_id=cfg.forwarding_chat,
        text=f"@{message.from_user.username}, `{message.from_user.full_name}`\n\n"
        f"*1️⃣ Топик:* `Другое`\n"
        f"*2️⃣ Информация:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
    )
    await state.clear()


@router.message(Question.position, ~F.text)
@router.message(Question.info, ~F.text)
@router.message(Material.descr, ~F.text)
@router.message(Material.info, ~F.text)
@router.message(Interview.position, ~F.text)
@router.message(Interview.company, ~F.text)
@router.message(Interview.info, ~F.text)
@router.message(Other.info, ~F.text)
async def incorrect_text(message: types.Message) -> None:
    await message.answer(text=not_text_message, reply_markup=return_to_menu)
