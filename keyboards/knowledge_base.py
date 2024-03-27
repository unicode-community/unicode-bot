from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import AdditionalButtons, UnicodeButtons, UnicodeLinks

redirect_knowdledge_base_and_update_base_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.redirect_to_knowledge_base, url=UnicodeLinks.knowdledge_base)],
        [InlineKeyboardButton(text=AdditionalButtons.update_knowdledge_base, callback_data="update_knowledge_base")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


information_options = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❔ Вопросы с собеседования", callback_data="add_questions")],
        [InlineKeyboardButton(text="💎 Полезные материалы", callback_data="add_materials")],
        [InlineKeyboardButton(text="📋 Резюме собеса", callback_data="add_summary")],
        [InlineKeyboardButton(text="🤔 Другое", callback_data="add_other")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)
