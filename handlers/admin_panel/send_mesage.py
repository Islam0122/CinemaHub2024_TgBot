import logging

from aiogram import Bot, F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaDocument, InputMediaPhoto
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputMediaVideo
from aiogram.utils.markdown import bold, italic, code
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_users
from filter.chat_types import ChatTypeFilter, IsAdmin

send_message_private_router = Router()
send_message_private_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")],
    ],
    resize_keyboard=True,
)


class SendMessageState(StatesGroup):
    WaitingForReview = State()


@send_message_private_router.message(Command("send_message"))
async def start_send_message_to_all_users(message: types.Message, state: FSMContext):
    await state.set_state(SendMessageState.WaitingForReview)
    await message.answer("📢 Введите текст сообщения, который вы хотите отправить всем пользователям.",
                         reply_markup=keyboard)

@send_message_private_router.message(SendMessageState.WaitingForReview)
async def send_message_to_all_users(message: types.Message, state: FSMContext, bot: Bot,session:AsyncSession):
    users = await orm_get_users(session)
    for user in users:
        user_id = user.telegram_id

        if user_id not in bot.my_admins_list:
            if message.document:
                file_id = message.document.file_id
                caption = message.caption
                await bot.send_media_group(user_id, media=[types.InputMediaDocument(media=file_id, caption=caption)])
                await state.clear()
            elif message.photo:
                file_id = message.photo[-1].file_id  # Берем последнюю фотографию из массива фотографий
                caption = message.caption
                await bot.send_media_group(user_id, media=[types.InputMediaPhoto(media=file_id, caption=caption)])
                await state.clear()
            elif message.voice:
                file_id = message.voice.file_id
                caption = message.caption
                await bot.send_media_group(user_id, media=[
                    types.InputMediaAudio(media=file_id, caption=caption)])
                await state.clear()
            elif message.video:
                file_id = message.video.file_id
                caption = message.caption
                await bot.send_media_group(user_id, media=[types.InputMediaVideo(media=file_id, caption=caption)])
                await state.clear()
            elif message.text:
                text = message.text
                await bot.send_message(user_id, text)
                await state.clear()
            else:
                continue

    await message.answer("✅ Сообщение успешно отправлено всем пользователям!",
                         reply_markup=ReplyKeyboardRemove())


@send_message_private_router.callback_query(F.data.startswith('send_message'))
async def send_message_command_callback_query(query: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    message = query.message
    await state.set_state(SendMessageState.WaitingForReview)
    await message.answer("📢 Введите текст сообщения, который вы хотите отправить всем пользователям.",
                         reply_markup=keyboard)
