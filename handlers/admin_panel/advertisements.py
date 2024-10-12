# from datetime import datetime
# import pytz
# from aiogram import types
# from aiogram.types import InlineKeyboardButton
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.cron import CronTrigger
# from apscheduler.triggers.interval import IntervalTrigger
# from sqlalchemy.ext.asyncio import AsyncSession
# from database.orm_query import orm_get_users
#
# timezone = pytz.timezone('Asia/Bishkek')  # Замените на вашу временную зону
#
# advertisements_1 = {
#     "image": "media/images/img_1.png",
#     "text": "🎉 Промо-акция на продукцию 1!",
#     "url": "https://www.google.com/"
# }
#
# advertisements_2 = {
#     "image": "media/images/img_1.png",
#     "text": "🔥 Промо-акция на продукцию 2!",
#     "url": "https://www.google.com/"
# }
#
# advertisements_3 = {
#     "image": "media/images/img_1.png",
#     "text": "🌟 Уникальное предложение на продукцию 3!",
#     "url": "https://www.google.com/"
# }
#
#
# async def send_advertisement(user_id, advertisement, bot):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.add(InlineKeyboardButton( text='Узнать больше',
#                                        url=advertisement['url'])) # Исправлено
#     await bot(
#         chat_id=user_id,
#         photo=types.FSInputFile(advertisement['image']),
#         caption=f"{advertisement['text']}",
#         parse_mode='Markdown',
#         reply_markup=keyboard.as_markup()
#     )
#
#
# async def send_advertisements(session, advertisement, bot):
#     users = await orm_get_users(session)
#     for user in users:
#         await send_advertisement(user.telegram_id,advertisement= advertisement,bot=bot)
#
#
# async def schedule_advertisements(session, bot):
#     scheduler = AsyncIOScheduler()
#
#     scheduler.add_job(
#         send_advertisements,
#         IntervalTrigger(seconds=2, start_date=datetime.now(timezone)),
#         args=[session, advertisements_1, bot]  # Передаем bot
#     )
#
#     # Запланируйте отправку объявлений в определенные дни и время
#     scheduler.add_job(
#         send_advertisements,
#         CronTrigger(day_of_week='mon, wed, fri', hour=8, minute=0),
#         args=[session, advertisements_1, bot]
#     )
#
#     scheduler.add_job(
#         send_advertisements,
#         CronTrigger(day_of_week='sun, fri, wed', hour=20, minute=0),
#         args=[session, advertisements_2, bot]
#     )
#
#     scheduler.add_job(
#         send_advertisements,
#         CronTrigger(day_of_week='mon, wed, fri', hour=16, minute=0),
#         args=[session, advertisements_3, bot]
#     )
#     scheduler.start()
#
