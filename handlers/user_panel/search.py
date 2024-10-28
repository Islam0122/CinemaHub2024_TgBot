import requests
from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_cinema_by_code
from filter.chat_types import ChatTypeFilter, is_subscribed_filter
from handlers.user_panel.parser_functions import search_movie_by_name, search_movie_by_code
from handlers.user_panel.start_functions import user_preferences
from keyboard.inline import return_inline_keyboard
from message_text.text import messages
from bs4 import BeautifulSoup as BS

search_private_router = Router()
search_private_router.message.filter(ChatTypeFilter(['private']))


class SearchState(StatesGroup):
    search = State()


@search_private_router.callback_query(F.data == 'search_by_name',is_subscribed_filter)
async def search_by_name(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    language = user_preferences.get(query.from_user.id, {}).get('language', 'en')
    await query.message.answer(text=messages[language]['enter_movie_name'])
    await state.set_state(SearchState.search)


@search_private_router.message(SearchState.search)
async def process_search_by_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'en')
    movie_name = message.text.strip()  # Получаем введённое название фильма
    movie_results = search_movie_by_name(movie_name)

    if movie_results:
        keyboard = InlineKeyboardBuilder()
        for movie in movie_results:
            keyboard.add(
                InlineKeyboardButton(text=movie['title'], url=movie['url']),
            )
        keyboard.add(
            InlineKeyboardButton(text=messages[language]['return'], callback_data="start"),
        )
        await message.answer(
                messages[language]['movie_found'],
                reply_markup=keyboard.as_markup(),
            )
    else:
        await message.answer(messages[language]['movie_not_found'],reply_markup=return_inline_keyboard(language),)
    await state.clear()


@search_private_router.callback_query(F.data == 'search_by_code',is_subscribed_filter)
async def search_by_code(query: types.CallbackQuery):
    await query.message.delete()
    language = user_preferences.get(query.from_user.id, {}).get('language', 'en')
    await query.message.answer(messages[language]['enter_cinema_code'], reply_markup=return_inline_keyboard(language))


@search_private_router.message(F.text.startswith('/search_by_code'))
async def search_by_code_command(message: types.Message, session: AsyncSession):
    language = user_preferences.get(message.from_user.id, {}).get('language', 'en')
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.answer(messages[language]['enter_cinema_code'])  # Сообщение с просьбой ввести код
        return
    cinema_code = command_parts[1].strip()
    cinema = await orm_get_cinema_by_code(session, cinema_code)

    if cinema:
        movie_name = cinema.cinema_name
        movie_results = search_movie_by_code(movie_name)

        if movie_results:
            for movie in movie_results:
                keyboard = InlineKeyboardBuilder()
                keyboard.add(
                    InlineKeyboardButton(text=messages[language]['watch'], url=movie['url']),
                )
                await message.answer(
                    f"{movie['url']}",
                    reply_markup=keyboard.as_markup(),
                )
            await message.answer(messages[language]['greeting'].format(name=message.from_user.full_name),
                                 reply_markup=return_inline_keyboard(language),
                                 )
        else:
            await message.answer(
                messages[language]['cinema_not_found'],  # Сообщение о том, что кинотеатр не найден
                reply_markup=return_inline_keyboard(language),
            )
    else:
        await message.answer(
            messages[language]['cinema_not_found'],  # Сообщение о том, что кинотеатр не найден
            reply_markup=return_inline_keyboard(language),
        )