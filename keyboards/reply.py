from aiogram.types import KeyboardButtonPollType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


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