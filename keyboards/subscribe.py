from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import SubscriptionsButtons, UnicodeButtons

choice_subscr_type_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=SubscriptionsButtons.unicode_guest, callback_data="unicode_guest"),
            InlineKeyboardButton(text=SubscriptionsButtons.unicode_starter, callback_data="unicode_starter")
        ],
        [InlineKeyboardButton(text=SubscriptionsButtons.unicode_base, callback_data="unicode_base")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)

choice_subscr_type_and_break_subscr_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=SubscriptionsButtons.unicode_guest, callback_data="unicode_guest"),
            InlineKeyboardButton(text=SubscriptionsButtons.unicode_starter, callback_data="unicode_starter")
        ],
        [InlineKeyboardButton(text=SubscriptionsButtons.unicode_base, callback_data="unicode_base")],
        [InlineKeyboardButton(text=SubscriptionsButtons.break_subscr, callback_data="break_subscr")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)

confirm_break_subscr_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=SubscriptionsButtons.confirm_break_subscr, callback_data="confirm_break_subscr")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


check_payment_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=SubscriptionsButtons.check_payment, callback_data="check_payment")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


def create_kb_to_payment(url: str, payment_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=SubscriptionsButtons.pay_subscr, url=url)],
            [InlineKeyboardButton(text=SubscriptionsButtons.check_payment, callback_data=f"check_payment_{payment_id}")],
            [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
        ]
    )
