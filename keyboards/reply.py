from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Оформить подписку"),
            KeyboardButton(text="База вопросов"),
            KeyboardButton(text="Бот для IT-знакомств"),
            KeyboardButton(text="База менторов"),
            KeyboardButton(text="Чаты сообщества"),
        ]
    ],
    resize_keyboard=True,
)
