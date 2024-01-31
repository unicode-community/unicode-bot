from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import CommandStart
from keyboards.builders import reply_builder
from messages import questions_welcome, link_to_questions_base
from db.database import Database
from datetime import datetime
from aiogram.fsm.context import FSMContext
from utils.states import Question, Material, Interview


router = Router()

@router.message(F.text.lower() == "база вопросов")
async def knowledge_base(message: types.Message, db: Database) -> None:
    await message.answer(
        text=questions_welcome,
        reply_markup=reply_builder(["Пополнить базу", "Перейти в базу", "В главное меню"])
    )
    
    user_info = await db.get_subscriber(user_id=message.from_user.id)
    
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)


@router.message(F.text.lower() == "перейти в базу")
async def redirect_knowledge_base(message: types.Message) -> None:
    await message.answer(
        text=link_to_questions_base, 
        reply_markup=reply_builder(text=["В главное меню"]),
        disable_web_page_preview=False
    )
    

@router.message(F.text.lower() == "пополнить базу")
async def topic_knowledge_base(message: types.Message, db: Database, state: FSMContext) -> None:
    await message.answer(
        text="Выбери, что ты хочешь прислать",
        reply_markup=reply_builder(
            text=["Список вопросов", "Полезные материалы", "Резюме собеса", "В главное меню"],
            sizes=[3, 1]
        )
    )
    await state.set_state()


@router.message(F.text == "Список вопросов")
async def topic_questions(message: types.Message, db: Database, state: FSMContext) -> None:
    await message.answer(text="Напиши на какую должность ты хочешь прислать вопросы (например: `Python Developer`, `IOS Developer`, `Data Science` etc.)")
    await state.update_data(topic="Список вопросов")
    await state.set_state(Question.position)
    

@router.message(Question.position, F.text)
async def position_questions(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer(text="Теперь пришли сам список вопросов одним сообщением")
    await state.set_state(Question.info)
    

@router.message(Question.info, F.text)
async def info_questions(message: types.Message, state: FSMContext) -> None:
    await state.update_data(info=message.text)
    
    data = await state.get_data()
    await message.answer(text=f"Топик: {data['topic']}\nПозиция: {data['position']}\nВопросы: {data['info']}")
    
    await message.answer(
        text="Модераторы проверят вопросы и внесут их в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )


@router.message(F.text == "Полезные материалы")
async def topic_materials(message: types.Message, db: Database, state: FSMContext) -> None:
    await message.answer(text="Пожалуйста, опиши, что за материалы ты хочешь прислать")
    await state.update_data(topic="Полезные материалы")
    await state.set_state(Material.descr)
    

@router.message(Material.descr, F.text)
async def descr_materials(message: types.Message, state: FSMContext) -> None:
    await state.update_data(descr=message.text)
    await message.answer(text="Теперь пришли ссылку (можно несколько, но одним сообщением)")
    await state.set_state(Material.info)


@router.message(Material.info, F.text)
async def info_materials(message: types.Message, state: FSMContext) -> None:
    await state.update_data(info=message.text)
    
    data = await state.get_data()
    await message.answer(text=f"Топик: {data['topic']}\nОписание: {data['descr']}\nМатериалы: {data['info']}")
    
    await message.answer(
        text="Модераторы проверят твои ссылки и внесут их в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )
    
    
    
@router.message(F.text == "Резюме собеса")
async def topic_interviews(message: types.Message, db: Database, state: FSMContext) -> None:
    await message.answer(text="Пожалуйста, напиши на какую должность ты хочешь прислать выжимку (например: `Python Developer`, `IOS Developer`, `Data Science` etc.)")
    await state.update_data(topic="Резюме собеса")
    await state.set_state(Interview.position)
    

@router.message(Interview.position, F.text)
async def position_interviews(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer(text="В какую компанию это собеседование?", reply_markup=reply_builder(["Это секрет"]))
    await state.set_state(Interview.company)


@router.message(Interview.company, F.text)
async def company_interviews(message: types.Message, state: FSMContext) -> None:
    await state.update_data(company=message.text)
    await message.answer(text="Теперь пришли выжимку собеседования одним сообщением")
    await state.set_state(Interview.info)


@router.message(Interview.info, F.text)
async def info_interviews(message: types.Message, state: FSMContext) -> None:
    await state.update_data(info=message.text)
    
    data = await state.get_data()
    await message.answer(text=f"Топик: {data['topic']}\nДолжность: {data['position']}\nКомпания: {data['company']}\nВыжимка: {data['info']}")
    
    await message.answer(
        text="Модераторы проверят твои вопросы и внесут их в базу. Спасибо, что вносишь вклад в наше сообщество!",
        reply_markup=reply_builder(["В главное меню"])
    )