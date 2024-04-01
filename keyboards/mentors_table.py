from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import AdditionalButtons, SubscriptionsButtons, UnicodeButtons, UnicodeLinks

redirect_to_mentors_table_and_become_mentor_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.redirect_to_mentors_table, url=UnicodeLinks.mentors_table)],
        [InlineKeyboardButton(text=AdditionalButtons.become_mentor, callback_data="become_mentor")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)

def create_redirect_to_mentors_table_and_subscribe_and_return_to_menu(
    url: str,
    payment_id: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=AdditionalButtons.redirect_to_mentors_table, url=UnicodeLinks.mentors_table)],
            [InlineKeyboardButton(text=SubscriptionsButtons.pay_subscr, url=url)],
            [InlineKeyboardButton(text=SubscriptionsButtons.check_payment, callback_data=f"check_payment_{payment_id}")],
            [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
        ]
    )

fill_mentor_form_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.fill_mentor_form, callback_data="fill_mentor_form")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)

edit_and_delete_mentor_form_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.edit_mentor_form, callback_data="fill_mentor_form")],
        [InlineKeyboardButton(text=AdditionalButtons.delete_mentor_form, callback_data="delete_mentor_form")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)

confirm_delete_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.confirm_delete_form, callback_data="confirm_delete_mentor_form")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)

free_price_and_return_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=AdditionalButtons.free, callback_data="free_price")],
        [InlineKeyboardButton(text=UnicodeButtons.main_menu, callback_data="unicode_menu")],
    ]
)



def create_approve_or_reject_mentor_form(tg_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_mentor_{tg_id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_mentor_{tg_id}")],
        ],
    )


def create_delete_mentor(tg_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_mentor_{tg_id}")],
        ],
    )
