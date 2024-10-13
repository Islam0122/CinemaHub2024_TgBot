import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv, find_dotenv

from common.bot_cmds_list import private
from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from aiohttp import web

# Загрузим переменные окружения из .env
load_dotenv(find_dotenv())

# Импортируем ваши обработчики
from handlers.admin_panel.admin_start_functions import admin_start_functions_private_router
from handlers.admin_panel.send_mesage import send_message_private_router
from handlers.group_panel.user_group_private import user_group_router
from handlers.user_panel.recommendations_functions import recommendations_private_router
from handlers.user_panel.review_functions import review_private_router
from handlers.user_panel.search import search_private_router
from handlers.user_panel.start_functions import start_functions_private_router
from handlers.user_panel.unknown_functions import unknown_private_router

# Получаем токен бота и ID группы
TOKEN = os.getenv('TOKEN')
GROUP_ID = os.getenv('group_id')

# Настраиваем прокси, если нужно
session = AiohttpSession(proxy="http://proxy.server:3128")

# Инициализируем бота и диспетчер
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
bot.my_admins_list = []
bot.group_id = GROUP_ID

dp = Dispatcher()

# Включаем роутеры
dp.include_router(start_functions_private_router)
dp.include_router(admin_start_functions_private_router)
dp.include_router(send_message_private_router)
dp.include_router(search_private_router)
dp.include_router(review_private_router)
dp.include_router(recommendations_private_router)
dp.include_router(user_group_router)
dp.include_router(unknown_private_router)

# Функция, которая будет выполнена при старте
async def on_startup():
    run_param = False  # Переменная для дропа базы
    if run_param:
        await drop_db()  # Удаление БД
    await create_db()    # Создание БД
    print("Сервер успешно запущен! 😊 Привет, босс!")

# Функция, которая будет выполнена при остановке
async def on_shutdown():
    print("Сервер остановлен. 😔 Проверьте его состояние, босс!")

# Хэндлер для получения вебхуков
async def handle_webhook(request):
    request_body = await request.text()
    update = types.Update(**request.json())  # Преобразуем данные запроса в объект Update
    await dp.feed_update(bot, update)
    return web.Response()

# Главная функция
async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Добавляем middleware для работы с базой данных
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    # Настраиваем вебхук
    webhook_url = "https://cinemahub2024-tgbot.onrender.com/webhook"
    await bot.set_webhook(url=webhook_url)

    # Удаляем команды и устанавливаем новые
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())

    # Настраиваем веб-сервер для приёма вебхуков
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)

    # Запуск веб-сервера на порту, который предоставляет Render
    port = int(os.environ.get('PORT', 3000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    print(f"Сервер запущен на порту {port}")

    # Бесконечный цикл ожидания событий
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())