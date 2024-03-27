from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import AdditionalButtons, UnicodeButtons, UnicodeLinks

redirect_to_bot_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.redirect_to_networking_bot, url=UnicodeLinks.networking_bot)],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)
