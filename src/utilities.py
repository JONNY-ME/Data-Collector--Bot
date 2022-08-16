from aiogram import types 


def get_inine_markup(text_data:tuple) -> types.InlineKeyboardMarkup:
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)

    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_data)

    keyboard_markup.row(*row_btns)

    return keyboard_markup