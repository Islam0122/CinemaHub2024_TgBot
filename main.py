import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiohttp import web

from dotenv import find_dotenv, load_dotenv
from middlewares.db import DataBaseSession


load_dotenv(find_dotenv())


from handlers.admin_panel.admin_start_functions import admin_start_functions_private_router
from handlers.admin_panel.send_mesage import send_message_private_router
from handlers.group_panel.user_group_private import user_group_router
from common.bot_cmds_list import private
from aiogram.client.session.aiohttp import AiohttpSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_panel.recommendations_functions import recommendations_private_router

from handlers.user_panel.review_functions import review_private_router
from handlers.user_panel.search import search_private_router
from handlers.user_panel.start_functions import start_functions_private_router
from handlers.user_panel.unknown_functions import unknown_private_router

session = AiohttpSession(proxy="http://proxy.server:3128")

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
bot.my_admins_list = []
bot.group_id = os.getenv('group_id')

dp = Dispatcher()

dp.include_router(start_functions_private_router)
dp.include_router(admin_start_functions_private_router)
dp.include_router(send_message_private_router)
dp.include_router(search_private_router)
dp.include_router(review_private_router)
dp.include_router(recommendations_private_router)
dp.include_router(user_group_router)
dp.include_router(unknown_private_router)


async def on_startup():
    run_param = False
    if run_param:
        await drop_db()
    await create_db()
    # async with AsyncSession() as session:
    #     await advertisements.set_scheduler(session=session,bot=bot)
    print("Сервер успешно запущен! 😊 Привет, босс!")


async def on_shutdown():
    print("Сервер остановлен. 😔 Проверьте его состояние, босс!")


async def handle_webhook(request):
    update = await request.json()
    await dp.process_update(types.Update(**update))
    return web.Response(text="OK")


# Запуск приложения
async def main():
    # Регистрация функций запуска и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Миддлвары
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    # Установка вебхука
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    await bot.set_webhook(url=webhook_url)

    # Настройка команд бота
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())

    # Настройка сервера aiohttp для обработки вебхуков
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)

    # Запуск вебсервера
    port = int(os.getenv('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    print(f"Сервер запущен на порту {port}")

    # Запуск polling
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())