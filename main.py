import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from config.config import TG_TOKEN_DEV

__all__ = []


bot = Bot(TG_TOKEN_DEV)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> Message:
    text_answer = f"Привет {message.from_user.first_name}"
    await message.answer(text_answer)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
