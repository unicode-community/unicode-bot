from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подписка")],
        [KeyboardButton(text="База знаний"), KeyboardButton(text="Бот для IT-знакомств")],
        [KeyboardButton(text="База менторов"), KeyboardButton(text="Чаты сообщества")]
    ],
    resize_keyboard=True,
)
