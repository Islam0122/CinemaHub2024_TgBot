from aiogram import F,Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filter.chat_types import ChatTypeFilter
from handlers.user_panel.parser_functions import parse_movies
from handlers.user_panel.start_functions import user_preferences
from keyboard.inline import return_inline_keyboard
from message_text.text import messages

recommendations_private_router = Router()
recommendations_private_router.message.filter(ChatTypeFilter(['private']))


@recommendations_private_router.message(Command("recommendations"))
async def parsser(message: types.Message):
    bot = message.bot
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    language = user_preferences.get(user_id, {}).get('language', 'en')
    movies = parse_movies()  # Парсим данные один раз

    if not movies:
        await bot.send_message(
            user_id,
            text=messages[language]['recommendations_failed'],  reply_markup=return_inline_keyboard(language),
            parse_mode=ParseMode.HTML
        )
        return

    for movie in movies:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(text=messages[language]['watch'], url=movie['url'])
        )
        await bot.send_message(
            user_id,
            f"{movie['url']}",
            reply_markup=keyboard.as_markup(),  # Преобразуем клавиатуру в нужный формат
            parse_mode=ParseMode.HTML
        )

    await bot.send_message(
        user_id,
        messages[language]['greeting'].format(name=user_name),
        parse_mode=ParseMode.HTML
    )


@recommendations_private_router.callback_query(F.data.startswith("recommendations"))
async def recommendations(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    language = user_preferences.get(user_id, {}).get('language', 'en')
    movies = parse_movies()

    if not movies:
        await query.message.answer(text=messages[language]['recommendations_failed'],  reply_markup=return_inline_keyboard(language))
        await query.answer()  # Закрываем "часики"
        return

    for movie in movies:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(text=messages[language]['watch'], url=movie['url'])
        )
        await query.message.answer(
            f"{movie['url']}",
            reply_markup=keyboard.as_markup(),  # Преобразуем клавиатуру в нужный формат
            parse_mode=ParseMode.HTML
        )

    await query.message.answer(messages[language]['greeting'].format(name=user_name),
                               reply_markup=return_inline_keyboard(language),
                               )
    await query.answer()