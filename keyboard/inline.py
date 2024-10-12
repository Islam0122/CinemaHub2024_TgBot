from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from message_text.text import messages


def start_functions_keyboard(language: str):
    """Функция для создания клавиатуры выбора языка."""
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(text=messages[language]['search_kino'], callback_data='search_kino')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['recommendations'], callback_data='recommendations')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['leave_review'], callback_data='leave_review')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['our_channels'], callback_data='our_channels')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['about_bot'], callback_data='about_bot')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['instructions'], callback_data='instructions')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['select_language'], callback_data='select_language')
    )

    return keyboard.adjust(2,1,1,2).as_markup()


def language_selection_keyboard(language: str):
    """Функция для создания клавиатуры выбора языка."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_language_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_language_en"),
        InlineKeyboardButton(text=messages[language]['return'], callback_data="start"),
    )
    return keyboard.adjust(2).as_markup()


def return_inline_keyboard(language: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['search_kino'], callback_data='search_kino')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['recommendations'], callback_data='recommendations')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['return'], callback_data="start"),
    )
    return keyboard.adjust(2).as_markup()


def cancel_inline_keyboard(language: str) :
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['cancel'], callback_data="cancel_review"),
    )
    return keyboard.adjust().as_markup()
