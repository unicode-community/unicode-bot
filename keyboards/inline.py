from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from messages import link_to_mentors_base, link_to_networking_bot, link_to_questions_base

redirect_mentors_base = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Перейти в базу менторов", url=link_to_mentors_base)]]
)

redirect_knowdledge_base = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Перейти в базу знаний", url=link_to_questions_base)]]
)

redirect_networking_bot = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Перейти в бота", url=link_to_networking_bot)]]
)

unicode_chats = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="UNI: ФЛУДИЛКА", url="https://t.me/+Pphu6iu6VGwwYmRi")],
        [InlineKeyboardButton(text="UNI: резюме", url="https://t.me/+vLW1bN_CDE5iZWM6")],
        [InlineKeyboardButton(text="UNI: python", url="https://t.me/+3iec-KVDof4wZGIy")],
        [InlineKeyboardButton(text="UNI: data science", url="https://t.me/+-yVI9LU9klk2ZjJi")],
        [InlineKeyboardButton(text="UNI: база знаний", url="https://t.me/+UWs3Kbqu6uUzNWZi")]
    ]
)


def create_kb_to_payment(url: str, payment_id: str, subscription_type: str, extend: bool = False) -> InlineKeyboardMarkup:
    action = "Оплатить" if not extend else "Продлить"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"💵 {action} подписку {subscription_type}", url=url)],
            [InlineKeyboardButton(text="🔍 Проверить оплату", callback_data=f"check_payment_{payment_id}")]
        ]
    )
