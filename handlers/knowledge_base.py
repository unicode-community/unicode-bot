from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from dotenv import find_dotenv, load_dotenv

import messages.knowledge_base as messages
from db.database import Database
from keyboards.general import return_to_menu, subscribe_and_return_to_menu
from keyboards.knowledge_base import information_options, redirect_knowdledge_base_and_update_base_and_return_to_menu
from messages.general import not_text_message
from utils.states import Interview, Material, Other, Question
from utils.subscriptions import get_subscription_status

load_dotenv(find_dotenv())

router = Router()


@router.callback_query(F.data == "unicode_knowdledge_base")
async def knowledge_base(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    access_to_knowledge_base = (
        (subscriber_info["subscription_db_name"] is not None)
        and ("Доступ к базе знаний" in subscriber_info["subscription_features"])
    )

    if access_to_knowledge_base:
        await callback.message.answer(
            text=messages.welcome_knowledge_base,
            reply_markup=redirect_knowdledge_base_and_update_base_and_return_to_menu
        )
    else:
        await callback.message.answer(
            text=messages.welcome_knowledge_base + "\n" + messages.add_for_unsubscribers,
            reply_markup=subscribe_and_return_to_menu
        )


    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "update_knowledge_base")
async def update_knowledge_base(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(
        text=messages.ask_which_to_send,
        reply_markup=information_options
    )
    await callback.answer()


@router.callback_query(F.data == "add_questions")
async def add_questions(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        text=messages.ask_interview_position,
        reply_markup=return_to_menu
    )
    await callback.answer()
    await state.set_state(Question.position)


@router.message(Question.position, F.text)
async def add_questions_position(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer(
        text=messages.ask_interview_questions,
        reply_markup=return_to_menu
    )
    await state.set_state(Question.info)


@router.message(Question.info, F.text)
async def add_questions_info(message: types.Message, state: FSMContext) -> None:
    await state.update_data(info=message.text)
    await message.answer(
        text=messages.feedback_after_interview,
        reply_markup=return_to_menu
    )

    data = await state.get_data()

    await message.answer( # TODO Заменить на отправку в чат админки
        # chat_id=os.getenv("FORWADING_CHAT"),
        text=f"@{message.from_user.username}, `{message.from_user.full_name}`\n\n"
         f"*1️⃣ Топик:* `Вопросы с собеседования`\n"
         f"*2️⃣ Позиция:* `{data['position']}`\n"
         f"*3️⃣ Вопросы:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
    )
    await state.clear()


@router.callback_query(F.data == "add_materials")
async def add_materials(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        text=messages.ask_materials_descr,
        reply_markup=return_to_menu
    )
    await callback.answer()
    await state.set_state(Material.descr)


@router.message(Material.descr, F.text)
async def add_materials_descr(message: types.Message, state: FSMContext) -> None:
    await state.update_data(descr=message.text)
    await message.answer(
        text=messages.ask_materials_info,
        reply_markup=return_to_menu
    )
    await state.set_state(Material.info)


@router.message(Material.info, F.text)
async def add_materials_info(message: types.Message, state: FSMContext) -> None:
    await state.update_data(info=message.text)

    await message.answer(
        text=messages.feedback_after_materials,
        reply_markup=return_to_menu
    )

    data = await state.get_data()

    await message.answer( # TODO Заменить на отправку в чат админки
        # chat_id=os.getenv("FORWADING_CHAT"),
        text=f"@{message.from_user.username}, `{message.from_user.full_name}`\n\n"
         f"*1️⃣ Топик:* `Полезные материалы`\n"
         f"*2️⃣ Описание:*\n```\n{data['descr']}```\n"
         f"*3️⃣ Информация:*\n```\n{data['info']}```",
        disable_web_page_preview=True,
    )
    await state.clear()


@router.callback_query(F.data == "add_summary")
async def add_summary(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        text=messages.ask_summary_position,
        reply_markup=return_to_menu
    )
    await callback.answer()
    await state.set_state(Interview.position)


@router.message(Interview.position, F.text)
async def add_summary_position(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer(
        text=messages.ask_summary_company,
        reply_markup=return_to_menu
    )
    await state.set_state(Interview.company)


@router.message(Interview.company, F.text)
async def add_summary_company(message: types.Message, state: FSMContext) -> None:
    await state.update_data(company=message.text)
    await message.answer(
        text=messages.ask_summary,
        reply_markup=return_to_menu
    )
    await state.set_state(Interview.info)


@router.message(Interview.info, F.text)
async def add_summary_info(message: types.Message, state: FSMContext) -> None:
    await state.update_data(info=message.text)

    await message.answer(
        text=messages.feedback_after_summary,
        reply_markup=return_to_menu
    )

    data = await state.get_data()

    await message.answer( # TODO Заменить на отправку в чат админки
        # chat_id=os.getenv("FORWADING_CHAT"),
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
    await callback.message.answer(
        text=messages.ask_other_info,
        reply_markup=return_to_menu
    )
    await callback.answer()
    await state.set_state(Other.info)


@router.message(Other.info, F.text)
async def add_other_info(message: types.Message, state: FSMContext) -> None:
    await state.update_data(info=message.text)

    await message.answer(
        text=messages.feedback_after_other,
        reply_markup=return_to_menu
    )

    data = await state.get_data()

    await message.answer( # TODO Заменить на отправку в чат админки
        # chat_id=os.getenv("FORWADING_CHAT"),
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
    await message.answer(
        text=not_text_message,
        reply_markup=return_to_menu
    )
