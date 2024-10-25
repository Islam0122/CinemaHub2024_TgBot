from aiogram.filters import Filter, BaseFilter
from aiogram import types, Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums.chat_member_status import ChatMemberStatus


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.my_admins_list


class IsSubscribedFilter(BaseFilter):
    def __init__(self, chat_ids: list[int]) -> None:
        self.chat_ids = chat_ids  # Список ID каналов или групп для проверки подписки

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        # Переменная для отслеживания статуса подписки
        all_subscribed = True

        for chat_id in self.chat_ids:
            try:
                member = await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)
                if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                    all_subscribed = False  # Пользователь не подписан
                    break  # Прекращаем проверку, если нашли канал, на который не подписан
            except Exception as e:
                print(f"Ошибка при проверке подписки: {e}")
                all_subscribed = False  # Если ошибка, предположим, что не подписан

        # Если пользователь не подписан на все каналы, отправляем сообщение
        if not all_subscribed:
            try:
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
                    chat_id=message.from_user.id,
                    text=(
                        "\n*Пожалуйста, подпишитесь на наши каналы:*\n"
                        "_Это важно для продолжения работы с ботом!_\n"
                        "*Please subscribe to our channels:*"
                        "\n_This is important for continuing to work with the bot!_"
                    ),
                    reply_markup=keyboard.as_markup(),
                    parse_mode="Markdown"
                )

            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю: {e}")

        return all_subscribed


SUBSCRIPTION_CHAT_IDS = [
    -1002465814665,
]

is_subscribed_filter = IsSubscribedFilter(chat_ids=SUBSCRIPTION_CHAT_IDS)
