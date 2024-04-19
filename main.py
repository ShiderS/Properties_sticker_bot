from typing import Union

from aiogram import Bot, Dispatcher, types
import asyncio

from aiogram.types import ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember, ChatMemberRestricted, \
    ChatMemberLeft, ChatMemberBanned

CHANNEL_ID = '@DRAGTIMES_RU'

bot = Bot(token="5731308348:AAHAYI-eMow-FrO83L3949QQyaZOS9wAK0Y")
dp = Dispatcher()

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="5731308348:AAHAYI-eMow-FrO83L3949QQyaZOS9wAK0Y")
CHANNEL_ID = '@teststupidbot69'
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status.value == 'member' or member.status.value == 'creator' or \
                member.status.value == 'administrator':
            await message.answer("Вы подписаны на канал")
        else:
            await message.answer("Вы не подписаны на канал")
    except Exception as e:
        await message.answer("Произошла ошибка при проверке подписки")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())