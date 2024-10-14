import asyncio
from aiogram import F, Router, types, Bot
from filter.chat_types import ChatTypeFilter, IsAdmin, is_subscribed_filter

from handlers.user_panel.start_functions import user_preferences
from message_text.text import messages

unknown_private_router = Router()
unknown_private_router.message.filter(ChatTypeFilter(['private']))


@unknown_private_router.message()
async def unknown_command(message: types.Message):
    await message.delete()
    user_id = message.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}

    language = user_preferences[user_id]['language']
    response_message = messages[language]['unknown_command']

    m=await message.answer(response_message)
    await asyncio.sleep(3)
    await m.delete()

