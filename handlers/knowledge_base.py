import os
from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv

from db.database import Database
from keyboards.builders import reply_builder
from keyboards.inline import redirect_knowdledge_base
from messages import error_no_subscr_for_knowdledge_base, knowdledge_base_welcome
from utils.states import Interview, Material, Question

load_dotenv(find_dotenv())

router = Router()

@router.message(F.text.lower() == "база знаний")
async def knowledge_base(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="🦄",
        reply_markup=reply_builder(["Пополнить базу", "В главное меню"], sizes=[1, 1])
    )
    await message.answer(
        text=knowdledge_base_welcome,
        reply_markup=redirect_knowdledge_base
    )


@router.message(F.text.lower() == "пополнить базу")
async def topic_knowledge_base(message: types.Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_base_subscriber = (user_info is not None) and (user_info.subscription_type == "unicode_base") and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if is_base_subscriber:
        await message.answer(
            text="Выбери, что ты хочешь прислать",
            reply_markup=reply_builder(
                text=["Список вопросов", "Полезные материалы", "Резюме собеса", "В главное меню"],
                sizes=[3, 1]
            )
        )
    else:
        buttons = ["Изменить подписку", "В главное меню"] if user_info.subscription_type == "unicode_guest" else ["Оформить подписку", "В главное меню"]
        await message.answer(
            text=error_no_subscr_for_knowdledge_base,
            reply_markup=reply_builder(text=buttons, sizes=[1, 1])
        )


@router.message(F.text == "Список вопросов")
async def topic_questions(message: types.Message, state: FSMContext, db: Database) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_base_subscriber = (user_info is not None) and (user_info.subscription_type == "unicode_base") and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if is_base_subscriber:
        await message.answer(
            text="Напиши на какую должность ты хочешь прислать вопросы (например: `Python Developer`, `IOS Developer`, `Data Science` etc.)",
            reply_markup=reply_builder(["В главное меню"])
        )
        await state.update_data(topic="Список вопросов")
        await state.set_state(Question.position)
    else:
        buttons = ["Изменить подписку", "В главное меню"] if user_info.subscription_type == "unicode_guest" else ["Оформить подписку", "В главное меню"]
        await message.answer(
            text=error_no_subscr_for_knowdledge_base,
            reply_markup=reply_builder(text=buttons, sizes=[1, 1])
        )
        await state.clear()


@router.message(Question.position, F.text)
async def position_questions(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer(
        text="Теперь пришли сам список вопросов одним сообщением",
        reply_markup=reply_builder(["В главное меню"])
    )
    await state.set_state(Question.info)


@router.message(Question.info, F.text)
async def info_questions(message: types.Message, bot: Bot, state: FSMContext) -> None:
    await state.update_data(info=message.text)

    await message.answer(
        text="🔍 Модераторы проверят вопросы и внесут их в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )

    data = await state.get_data()
    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"*Прислал пользователь:* @{message.from_user.username}, `{message.from_user.full_name}`\n\n"
         f"*1️⃣ Топик:* `{data['topic']}`\n"
         f"*2️⃣ Позиция:* `{data['position']}`\n"
         f"*3️⃣ Вопросы:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
        parse_mode="MarkdownV2"
    )
    await state.clear()


@router.message(F.text == "Полезные материалы")
async def topic_materials(message: types.Message, state: FSMContext, db: Database) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_base_subscriber = (user_info is not None) and (user_info.subscription_type == "unicode_base") and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if is_base_subscriber:
        await message.answer(
            text="Пожалуйста, опиши, что за материалы ты хочешь прислать",
            reply_markup=reply_builder(["В главное меню"])
        )
        await state.update_data(topic="Полезные материалы")
        await state.set_state(Material.descr)
    else:
        buttons = ["Изменить подписку", "В главное меню"] if user_info.subscription_type == "unicode_guest" else ["Оформить подписку", "В главное меню"]
        await message.answer(
            text=error_no_subscr_for_knowdledge_base,
            reply_markup=reply_builder(text=buttons, sizes=[1, 1])
        )
        await state.clear()


@router.message(Material.descr, F.text)
async def descr_materials(message: types.Message, state: FSMContext) -> None:
    await state.update_data(descr=message.text)
    await message.answer(
        text="Теперь пришли ссылку (можно несколько, но одним сообщением)",
        reply_markup=reply_builder(["В главное меню"])
    )
    await state.set_state(Material.info)


@router.message(Material.info, F.text)
async def info_materials(message: types.Message, bot: Bot, state: FSMContext) -> None:
    await state.update_data(info=message.text)

    await message.answer(
        text="🔗 Модераторы проверят твои ссылки и внесут в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )

    data = await state.get_data()
    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"*Прислал пользователь:* @{message.from_user.username}, `{message.from_user.full_name}`\n\n"
         f"*1️⃣ Топик:* `{data['topic']}`\n"
         f"*2️⃣ Описание:*\n```\n{data['descr']}```\n"
         f"*3️⃣ Материалы:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
        parse_mode="MarkdownV2"
    )
    await state.clear()


@router.message(F.text == "Резюме собеса")
async def topic_interviews(message: types.Message, state: FSMContext, db: Database) -> None:
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    is_base_subscriber = (user_info is not None) and (user_info.subscription_type == "unicode_base") and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    if is_base_subscriber:
        await message.answer(
            text="Пожалуйста, напиши на какую должность ты хочешь прислать выжимку (например: `Python Developer`, `IOS Developer`, `Data Science` etc.)",
            reply_markup=reply_builder(["В главное меню"])
        )
        await state.update_data(topic="Резюме собеса")
        await state.set_state(Interview.position)
    else:
        buttons = ["Изменить подписку", "В главное меню"] if user_info.subscription_type == "unicode_guest" else ["Оформить подписку", "В главное меню"]
        await message.answer(
            text=error_no_subscr_for_knowdledge_base,
            reply_markup=reply_builder(text=buttons, sizes=[1, 1])
        )
        await state.clear()


@router.message(Interview.position, F.text)
async def position_interviews(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer(
        text="В какую компанию это собеседование?",
        reply_markup=reply_builder(["Это секрет", "В главное меню"], sizes=[1, 1])
    )
    await state.set_state(Interview.company)


@router.message(Interview.company, F.text)
async def company_interviews(message: types.Message, state: FSMContext) -> None:
    await state.update_data(company=message.text)
    await message.answer(
        text="Теперь пришли выжимку собеседования одним сообщением",
        reply_markup=reply_builder(["В главное меню"])
    )
    await state.set_state(Interview.info)


@router.message(Interview.info, F.text)
async def info_interviews(message: types.Message, bot: Bot, state: FSMContext) -> None:
    await state.update_data(info=message.text)

    await message.answer(
        text="🔍 Модераторы проверят вопросы и внесут их в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )

    data = await state.get_data()
    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"*Прислал пользователь:* @{message.from_user.username}, `{message.from_user.full_name}`\n\n"
         f"*1️⃣ Топик:* `{data['topic']}`\n"
         f"*2️⃣ Должность:* `{data['position']}`\n"
         f"*3️⃣ Компания:* `{data['company']}`\n"
         f"*4️⃣ Выжимка:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
        parse_mode="MarkdownV2"
    )
    await state.clear()
