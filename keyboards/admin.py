from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import UnicodeButtons

admin_functions = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Рассылка сообщений", callback_data="admin_send_messages")],
        [InlineKeyboardButton(text="Выдать подписку", callback_data="admin_give_subscription")],
        [InlineKeyboardButton(text="Отобрать подписку", callback_data="admin_remove_subscription")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


send_messages_segments = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Подписчики", callback_data="send_subscribers")],
        [InlineKeyboardButton(text="Только менторы", callback_data="send_mentors")],
        [InlineKeyboardButton(text="Все остальные", callback_data="send_others")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


def give_or_delete_subscription(tg_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Выдать подписку", callback_data=f"give_subscription_{tg_id}")],
            [InlineKeyboardButton(text="Удалить подписку", callback_data=f"remove_subscription_{tg_id}")],
            [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
        ]
    )


def confirm_remove_subscription(tg_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить удаление", callback_data=f"confirm_remove_subscription_{tg_id}")],
            [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
        ]
    )
