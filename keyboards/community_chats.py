from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import AdditionalButtons, UnicodeButtons

create_new_chat_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.create_new_chat, callback_data="create_new_chat")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


accept_create_new_chat_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.accept_create_new_chat, callback_data="accept_create_new_chat")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)
