from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import SubscriptionsButtons, UnicodeButtons

break_subscr_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
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

pay_subscr_and_write_to_support_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=SubscriptionsButtons.pay_subscr, callback_data="pay_subscr")],
        [InlineKeyboardButton(text=UnicodeButtons.support, callback_data="unicode_support")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)


def create_kb_to_payment(
    url: str,
    payment_id: str,
    add_write_support: bool = False
) -> InlineKeyboardMarkup:
    payment_kb = []
    payment_kb.append([InlineKeyboardButton(text=SubscriptionsButtons.pay_subscr, url=url)])
    if add_write_support:
        payment_kb.append([InlineKeyboardButton(text=UnicodeButtons.support, callback_data="unicode_support")])
    payment_kb.append([InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")])

    return InlineKeyboardMarkup(
        inline_keyboard=payment_kb
    )

