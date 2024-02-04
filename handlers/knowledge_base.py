import os

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv

from keyboards.builders import reply_builder
from messages import link_to_questions_base, questions_welcome
from utils.states import Interview, Material, Question

load_dotenv(find_dotenv())

router = Router()

@router.message(F.text.lower() == "база вопросов")
async def knowledge_base(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=questions_welcome,
        reply_markup=reply_builder(["Пополнить базу", "Перейти в базу", "В главное меню"])
    )


@router.message(F.text.lower() == "перейти в базу")
async def redirect_knowledge_base(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=link_to_questions_base,
        reply_markup=reply_builder(text=["В главное меню"]),
        disable_web_page_preview=False
    )


@router.message(F.text.lower() == "пополнить базу")
async def topic_knowledge_base(message: types.Message, state: FSMContext) -> None:
    state.clear()
    await message.answer(
        text="Выбери, что ты хочешь прислать",
        reply_markup=reply_builder(
            text=["Список вопросов", "Полезные материалы", "Резюме собеса", "В главное меню"],
            sizes=[3, 1]
        )
    )


@router.message(F.text == "Список вопросов")
async def topic_questions(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        text="Напиши на какую должность ты хочешь прислать вопросы (например: `Python Developer`, `IOS Developer`, `Data Science` etc.)",
        reply_markup=reply_builder(["В главное меню"])
    )
    await state.update_data(topic="Список вопросов")
    await state.set_state(Question.position)


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
        text="Модераторы проверят вопросы и внесут их в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )

    data = await state.get_data()
    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"Прислал пользователь: @{message.from_user.username}, {message.from_user.full_name}\n\nТопик: {data['topic']}\nПозиция: {data['position']}\nВопросы:\n{data['info']}",
        disable_web_page_preview=True,
        parse_mode=None
    )
    await state.clear()


@router.message(F.text == "Полезные материалы")
async def topic_materials(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        text="Пожалуйста, опиши, что за материалы ты хочешь прислать",
        reply_markup=reply_builder(["В главное меню"])
    )
    await state.update_data(topic="Полезные материалы")
    await state.set_state(Material.descr)


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
        text="Модераторы проверят твои ссылки и внесут их в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )

    data = await state.get_data()
    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"Прислал пользователь: @{message.from_user.username}, {message.from_user.full_name}\n\nТопик: {data['topic']}\nОписание: {data['descr']}\nМатериалы:\n{data['info']}",
        disable_web_page_preview=True,
        parse_mode=None
    )
    await state.clear()


@router.message(F.text == "Резюме собеса")
async def topic_interviews(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        text="Пожалуйста, напиши на какую должность ты хочешь прислать выжимку (например: `Python Developer`, `IOS Developer`, `Data Science` etc.)",
        reply_markup=reply_builder(["В главное меню"])
    )
    await state.update_data(topic="Резюме собеса")
    await state.set_state(Interview.position)


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
        text="Модераторы проверят твои вопросы и внесут их в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )

    data = await state.get_data()
    await bot.send_message(
        chat_id=os.getenv("FORWADING_CHAT"),
        text=f"Прислал пользователь: @{message.from_user.username}, {message.from_user.full_name}\n\nТопик: {data['topic']}\nДолжность: {data['position']}\nКомпания: {data['company']}\nВыжимка:\n{data['info']}",
        disable_web_page_preview=True,
        parse_mode=None
    )
    await state.clear()
