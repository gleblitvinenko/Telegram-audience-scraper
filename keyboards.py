from aiogram import types

import text_templates as tt


def menu_keyboard(language: str) -> types.ReplyKeyboardMarkup:
    kb_buttons_list = [
        [
            types.KeyboardButton(text=f"{tt.scrape_chat.get(language)}"),
            types.KeyboardButton(text=f"{tt.scrape_channel.get(language)}"),
        ],
        [
            types.KeyboardButton(text=f"{tt.language.get(language)}"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=kb_buttons_list,
        input_field_placeholder=f"{tt.select_action_placeholder.get(language)}",
    )

    return keyboard


def languages_keyboard(language: str) -> types.ReplyKeyboardMarkup:
    kb_buttons_list = [
        [
            types.KeyboardButton(text=f"{tt.ru_lang.get(language)}"),
            types.KeyboardButton(text=f"{tt.ua_lang.get(language)}"),
        ],
    ]

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=kb_buttons_list,
        input_field_placeholder=f"{tt.language_placeholder.get(language)}",
    )

    return keyboard
