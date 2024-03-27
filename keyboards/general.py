from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import UnicodeButtons

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=UnicodeButtons.subscribe, callback_data="unicode_subscribe")],
        [InlineKeyboardButton(text=UnicodeButtons.chats, callback_data="unicode_chats")],
        [InlineKeyboardButton(text=UnicodeButtons.networking_bot, callback_data="unicode_networking")],
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

# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# from config import UnicodeButtons
# from messages import link_to_mentors_base, link_to_networking_bot, link_to_questions_base

# redirect_mentors_base = InlineKeyboardMarkup(
#     inline_keyboard=[[InlineKeyboardButton(text="Перейти в базу менторов", url=link_to_mentors_base)]]
# )

# redirect_knowdledge_base = InlineKeyboardMarkup(
#     inline_keyboard=[[InlineKeyboardButton(text="Перейти в базу знаний", url=link_to_questions_base)]]
# )

# redirect_networking_bot = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text=UnicodeButtons.networking_bot, url=link_to_networking_bot)],
#         [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")]
#     ]
# )

