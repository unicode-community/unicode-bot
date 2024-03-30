from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import UnicodeButtons
from utils import unicode_base, unicode_guest, unicode_starter

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
        [InlineKeyboardButton(text="Все пользователи бота", callback_data="send_all_users")],
        [InlineKeyboardButton(text="Все подписчики", callback_data="send_all_subscribers")],
        [InlineKeyboardButton(text=f"{unicode_guest.name} подписчики", callback_data="send_unicode_guest")],
        [InlineKeyboardButton(text=f"{unicode_starter.name} подписчики", callback_data="send_unicode_starter")],
        [InlineKeyboardButton(text=f"{unicode_base.name} подписчики", callback_data="send_unicode_base")],
        [InlineKeyboardButton(text="Менторы", callback_data="send_mentors")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


def give_or_delete_subscription(tg_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{unicode_guest.name}", callback_data=f"give_unicode_guest_{tg_id}")],
            [InlineKeyboardButton(text=f"{unicode_starter.name}", callback_data=f"give_unicode_starter_{tg_id}")],
            [InlineKeyboardButton(text=f"{unicode_base.name}", callback_data=f"give_unicode_base_{tg_id}")],
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
