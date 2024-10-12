from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from filter.chat_types import ChatTypeFilter, IsAdmin, is_subscribed_filter
from handlers.user_panel.start_functions import user_preferences
from keyboard.inline import return_inline_keyboard, cancel_inline_keyboard
from message_text.text import messages

review_private_router = Router()
review_private_router.message.filter(ChatTypeFilter(['private']))


class ReviewState(StatesGroup):
    WaitingForReview = State()


async def send_review(user, target):
    user_id = user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}

    language = user_preferences[user_id]['language']

    await target.answer(
        text=messages[language]['leave_review_message'],
        reply_markup=cancel_inline_keyboard(language)
    )


@review_private_router.message(Command("leave_review"),is_subscribed_filter)
async def send_review_request(message: types.Message, state: FSMContext):
    await send_review(message.from_user, message)
    await state.set_state(ReviewState.WaitingForReview)


@review_private_router.callback_query(F.data.startswith("leave_review"))
async def send_review_request_callback_query(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    await send_review(query.from_user, query.message)
    await state.set_state(ReviewState.WaitingForReview)


@review_private_router.message(ReviewState.WaitingForReview)
async def process_review(message: types.Message, state: FSMContext, bot: Bot):
    language = user_preferences.get(message.from_user.id, {}).get('language', 'ru')
    group_id = bot.group_id

    if message.text:
        user_info = f"{message.from_user.first_name}"
        if message.from_user.last_name:
            user_info += f" {message.from_user.last_name}"
        if message.from_user.username:
            user_info += f" (@{message.from_user.username})"
        review_text = message.text
        review_message = f"💬 Отзыв от {user_info}:\n\n{review_text}"
        await bot.send_message(chat_id=group_id, text=review_message)
        await message.answer(text=messages[language]['review_thanks'], reply_markup=return_inline_keyboard(language))
        await state.clear()
    else:
        await message.answer(text=messages[language]['review_invalid'], reply_markup=return_inline_keyboard(language))


@review_private_router.callback_query(F.data.startswith("cancel_review"))
async def cancel_review(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    user_id = query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await query.answer(text=messages[language]['review_cancelled'])
    await query.message.answer(text=messages[language]['cancel_review_message'],
                               reply_markup=return_inline_keyboard(language))
    await state.clear()

