from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import UnicodeButtons

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=UnicodeButtons.subscribe, callback_data="unicode_subscribe")],
        [InlineKeyboardButton(text=UnicodeButtons.private_channel, callback_data="unicode_private_channel")],
        [InlineKeyboardButton(text=UnicodeButtons.chats, callback_data="unicode_chats")],
        # [InlineKeyboardButton(text=UnicodeButtons.networking_bot, callback_data="unicode_networking")], # TODO включить когда будет нужно
        [InlineKeyboardButton(text=UnicodeButtons.knowdledge_base, callback_data="unicode_knowdledge_base")],
        [InlineKeyboardButton(text=UnicodeButtons.mentors_table, callback_data="unicode_mentors_table")],
        [InlineKeyboardButton(text=UnicodeButtons.support, callback_data="unicode_support")],
    ]
)


return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")]]
)


subscribe_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=UnicodeButtons.subscribe, callback_data="unicode_subscribe")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


write_to_support_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=UnicodeButtons.support, callback_data="unicode_support")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)
