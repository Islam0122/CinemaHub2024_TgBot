from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_delete_cinema_by_code, orm_add_cinema_by_code, orm_get_all_cinemas
from filter.chat_types import ChatTypeFilter, IsAdmin
from message_text.text import messages

admin_start_functions_private_router = Router()
admin_start_functions_private_router.message.filter(ChatTypeFilter(['private']), IsAdmin())


class CinemaStates(StatesGroup):
    waiting_for_cinema_code = State()
    waiting_for_cinema_name = State()
    waiting_for_cinema_delete = State()


def admin_start_functions_keyboard():
    keyboard = InlineKeyboardBuilder()
    add_cinema_button = InlineKeyboardButton(
        text='Добавить Кино code', callback_data='add_cinema_code'
    )
    delete_cinema_button = InlineKeyboardButton(
        text='Удалить Кино code', callback_data='delete_cinema_code'
    )
    keyboard.row(add_cinema_button)
    keyboard.row(delete_cinema_button)
    keyboard.add(
        InlineKeyboardButton(text="Список кино code", callback_data='list_cinema_code')
    )
    keyboard.add(
        InlineKeyboardButton(text="📢Рассылка сообщений ", callback_data="send_message")
    )

    return keyboard.adjust(2).as_markup()


def return_admin_start_functions_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Назад ", callback_data='admin_start')
    )

    return keyboard.adjust(1).as_markup()


async def send_welcome_message(user, target, photo_path='media/images/img_1.png'):
    welcome_text = (
        f"{user.full_name}! 😊\n\n"
        "Добро пожаловать в административный раздел бота.\n"
        "Выберите действие ниже:"
    )
    keyboard_markup = admin_start_functions_keyboard()
    await target.answer_photo(
        photo=types.FSInputFile(photo_path),
        caption=welcome_text,
        reply_markup=keyboard_markup
    )


@admin_start_functions_private_router.message(
    F.text.lower().contains('admin_start') | (F.text.lower() == 'admin_start'))
async def start_cmd(message: types.Message, session: AsyncSession):
    """Обработчик команды /admin_start"""
    await send_welcome_message(message.from_user, message)


@admin_start_functions_private_router.callback_query(F.data.startswith('admin_start'))
async def start_command_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    """Обработчик callback_query с командой admin_start"""
    await query.message.delete()
    await send_welcome_message(query.from_user, query.message)


@admin_start_functions_private_router.callback_query(F.data == 'list_cinema_code')
async def list_cinema_code_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    await query.message.delete()
    list_cinema_code = await orm_get_all_cinemas(session)
    if list_cinema_code:
        cinema_list_text = "🎬 *Список кино кодов:*\n\n"  # Заголовок
        for cinema in list_cinema_code:
            cinema_list_text += f"📽️ Код: `{cinema.cinema_code}` - Название: *{cinema.cinema_name}*\n"
    else:
        cinema_list_text = "❌ *Нет доступных кинотеатров.*"

    await query.message.answer(text=cinema_list_text, parse_mode=ParseMode.MARKDOWN,
                               reply_markup=return_admin_start_functions_keyboard())


@admin_start_functions_private_router.callback_query(F.data.startswith('add_cinema_code'))
async def add_cinema_code_callback(query: CallbackQuery, state: FSMContext):
    """Обработчик нажатия на кнопку 'Добавить Кинотеатр'"""
    await query.message.delete()
    await query.answer()
    # Клавиатура с кнопкой "Отмена"
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add")
    )
    await query.message.answer("Введите код кино:",reply_markup=keyboard.as_markup())
    await state.set_state(CinemaStates.waiting_for_cinema_code)


# Обработчик ввода кода кинотеатра для добавления
@admin_start_functions_private_router.message(CinemaStates.waiting_for_cinema_code)
async def process_cinema_code(message: types.Message, state: FSMContext):
    cinema_code = message.text.strip()

    # Клавиатура с кнопкой "Отмена"
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add")
    )

    await state.update_data(cinema_code=cinema_code)
    await message.answer("Введите название кино:", reply_markup=keyboard.as_markup())
    await state.set_state(CinemaStates.waiting_for_cinema_name)


@admin_start_functions_private_router.message(CinemaStates.waiting_for_cinema_name)
async def process_cinema_name(message: types.Message, state: FSMContext, session: AsyncSession):
    cinema_name = message.text.strip()
    data = await state.get_data()
    cinema_code = data.get('cinema_code')

    try:
        new_cinema = await orm_add_cinema_by_code(session, cinema_code, cinema_name)

        if new_cinema:
            await message.answer(
                f"Кино успешно добавлен:\nКод: {new_cinema.cinema_code}\nНазвание: {new_cinema.cinema_name}",reply_markup=return_admin_start_functions_keyboard()
            )
        else:
            await message.answer("Ошибка: Кино с таким кодом или названием уже существует.",
                                 reply_markup=return_admin_start_functions_keyboard())
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении кино: {str(e)}")

    await state.clear()


# Обработчик кнопки "Отмена" для добавления кинотеатра
@admin_start_functions_private_router.callback_query(F.data == 'cancel_add')
async def cancel_add_callback(query: CallbackQuery, state: FSMContext):
    """Обработчик отмены добавления кинотеатра"""
    await query.message.delete()
    await query.message.answer("Добавление отменено.",reply_markup=return_admin_start_functions_keyboard())
    await state.clear()


# Обработчик Callback Query для удаления кинотеатра
@admin_start_functions_private_router.callback_query(F.data.startswith('delete_cinema_code'))
async def delete_cinema_code_callback(query: CallbackQuery, state: FSMContext):
    """Обработчик нажатия на кнопку 'Удалить Кинотеатр'"""
    await query.message.delete()
    await query.answer()

    # Клавиатура с кнопкой "Отмена"
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")
    )

    await query.message.answer("Введите код кино, который хотите удалить:", reply_markup=keyboard.as_markup())
    await state.set_state(CinemaStates.waiting_for_cinema_delete)


# Обработчик кнопки "Отмена"
@admin_start_functions_private_router.callback_query(F.data == 'cancel_delete')
async def cancel_delete_callback(query: CallbackQuery, state: FSMContext):
    """Обработчик отмены удаления кинотеатра"""
    await query.message.delete()
    await query.message.answer("Удаление отменено.",
                               reply_markup=return_admin_start_functions_keyboard())
    await state.clear()


# Обработчик ввода кода кинотеатра для удаления
@admin_start_functions_private_router.message(CinemaStates.waiting_for_cinema_delete)
async def process_delete_cinema_code(message: types.Message, state: FSMContext, session: AsyncSession):
    cinema_code = message.text.strip()

    if cinema_code.lower() == "отмена":
        await message.answer('Удаление отменено.',reply_markup=return_admin_start_functions_keyboard())
        await state.clear()
    else:
        deleted_count = await orm_delete_cinema_by_code(session, cinema_code)

        if deleted_count:
            await message.answer(f"Кино с кодом {cinema_code} успешно удалено.",
                                 reply_markup=return_admin_start_functions_keyboard())
        else:
            await message.answer("Кино с таким кодом не найдено.",reply_markup=return_admin_start_functions_keyboard())

        await state.clear()

