from typing import List, Union

from aiogram.utils.keyboard import ReplyKeyboardBuilder


def reply_builder(
    text: Union[str, List[str]],
    sizes: Union[int, List[int]]=2,
    one_time_keyboard: bool=True,
    **kwargs
) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()

    if isinstance(text, str):
        text = [text]
    if isinstance(sizes, int):
        sizes = [sizes]

    for txt in text:
        builder.button(text=txt)

    builder.adjust(*sizes)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=one_time_keyboard, **kwargs)