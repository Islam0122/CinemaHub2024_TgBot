from aiogram import F, types, Router, Bot
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_user_by_telegram_id, orm_add_user
from filter.chat_types import ChatTypeFilter, is_subscribed_filter, SUBSCRIPTION_CHAT_IDS
from keyboard.inline import language_selection_keyboard, start_functions_keyboard, return_inline_keyboard
from message_text.text import messages

start_functions_private_router = Router()
start_functions_private_router.message.filter(ChatTypeFilter(['private']))
user_preferences = {}


async def send_welcome_message(user, target, session: AsyncSession, photo_path='media/images/img_1.png'):
    """Функция для отправки приветственного сообщения с фото."""
    user_id = user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'en'}

    language = user_preferences[user_id]['language']

    existing_user = await orm_get_user_by_telegram_id(session, user_id)

    if not existing_user:
        name = user.first_name
        username = f"@{user.username}" if user.username else ''
        await orm_add_user(session, telegram_id=user_id, full_name=name, username=username)
    keyboard_markup = start_functions_keyboard(language)
    await target.answer_photo(
        photo=types.FSInputFile(photo_path),
        caption=f"{user.full_name}! 😊\n\n{messages[language]['welcome']}",
        reply_markup=keyboard_markup
    )


@start_functions_private_router.message(CommandStart())
@start_functions_private_router.message(F.text.lower() == 'start')
async def start_cmd(message: types.Message, session: AsyncSession,bot:Bot):
    """Обработчик команды /start"""
    await send_welcome_message(message.from_user, message, session)


@start_functions_private_router.callback_query(F.data.startswith('start'))
async def start_command_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    """Обработчик callback_query с командой start"""
    await query.message.delete()
    await send_welcome_message(query.from_user, query.message, session)


@start_functions_private_router.message(Command("select_language"))
async def select_language(message: types.Message):
    """Обработчик команды выбора языка через сообщение"""
    user_id = message.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'en'}
    language = user_preferences[user_id]['language']
    keyboard = language_selection_keyboard(language)
    await message.answer(
        "Please select your language / Пожалуйста, выберите язык / Тилди тандаңыз:",
        reply_markup=keyboard
    )


@start_functions_private_router.callback_query(F.data == 'select_language')
async def select_language_callback(query: types.CallbackQuery):
    """Обработчик выбора языка через callback"""
    await query.message.delete()
    user_id = query.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'en'}

    language = user_preferences[user_id]['language']
    keyboard = language_selection_keyboard(language)
    await query.message.answer(
        "Please select your language / Пожалуйста, выберите язык 🤗 :",
        reply_markup=keyboard
    )


@start_functions_private_router.callback_query(F.data.startswith('set_language_'))
async def set_language_callback(query: types.CallbackQuery):
    """Обработчик установки языка через callback"""
    await query.message.delete()
    user_id = query.from_user.id

    # Если пользователь не существует, инициализируем его настройки
    if user_id not in user_preferences:
        user_preferences[user_id] = {}

    # Установка языка в зависимости от нажатой кнопки
    if query.data == "set_language_ru":
        user_preferences[user_id]['language'] = 'ru'
        response = "Язык установлен на русский."
    elif query.data == "set_language_en":
        user_preferences[user_id]['language'] = 'en'
        response = "Language set to English."

    language = user_preferences[user_id]['language']
    await query.message.answer(
        text=response,
        reply_markup=return_inline_keyboard(language)
    )


@start_functions_private_router.callback_query(F.data.startswith('our_channels'))
async def our_channels_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'en'}

    language = user_preferences[user_id]['language']
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text='Канал 1', url='https://t.me/cinema_hub2024')
    )
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['return'], callback_data="start")
    )
    keyboard.adjust(2, 1).as_markup()

    await query.message.edit_caption(
        caption=messages[language]['our_channels_message'],
        reply_markup=keyboard.as_markup(),
        parse_mode=ParseMode.MARKDOWN)


@start_functions_private_router.callback_query(F.data.startswith('about_bot'))
async def about_bot_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'en'}

    language = user_preferences[user_id]['language']
    await query.message.edit_caption(
        caption=messages[language]['about_bot_message'],
        reply_markup=return_inline_keyboard(language),
        parse_mode=ParseMode.MARKDOWN)


@start_functions_private_router.callback_query(F.data.startswith('instructions'))
async def instructions_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'en'}

    language = user_preferences[user_id]['language']
    await query.message.edit_caption(
        caption=messages[language]['instructions_message'],
        reply_markup=return_inline_keyboard(language),
        parse_mode=ParseMode.MARKDOWN)


@start_functions_private_router.callback_query(F.data.startswith('search_kino'))
async def search_kino_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'en'}
    language = user_preferences[user_id]['language']

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['search_by_name'], callback_data='search_by_name'),
        InlineKeyboardButton(text=messages[language]['search_by_code'], callback_data='search_by_code'),
        InlineKeyboardButton(text=messages[language]['return'], callback_data="start"),

    )

    await query.message.edit_caption(
        caption=messages[language]['choose_search_method'],
        reply_markup=keyboard.adjust(2, ).as_markup()
    )


@start_functions_private_router.callback_query(F.data == 'check_subscription')
async def check_subscription_callback(query: types.CallbackQuery, bot: Bot, session: AsyncSession):
    await query.message.delete()
    user_id = query.from_user.id
    all_subscribed = True

    for chat_id in SUBSCRIPTION_CHAT_IDS:
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                all_subscribed = False
                break
        except Exception as e:
            print(f"Error checking subscription: {e}")
            all_subscribed = False

    # Responding to the user in both languages
    if all_subscribed:
        await query.answer("You are subscribed to all channels! 🎉\nВы подписаны на все каналы! 🎉", show_alert=True)
        await send_welcome_message(query.from_user, query.message, session)
    else:
        # Sending the subscription buttons
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            types.InlineKeyboardButton(text='Канал 1', url='https://t.me/cinema_hub2024')
        )
        keyboard.add(
            types.InlineKeyboardButton(text='Check Subscription/Проверить подписку',
                                       callback_data='check_subscription'),
        )

        keyboard.adjust(1).as_markup()
        await bot.send_message(
            chat_id=user_id,
            text=(
                "\n*Пожалуйста, подпишитесь на наши каналы:*\n"
                "_Это важно для продолжения работы с ботом!_\n"
                "*Please subscribe to our channels:*"
                "\n_This is important for continuing to work with the bot!_"
            ),
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )
