import asyncio

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message

from config.config import TG_TOKEN_DEV

__all__ = []


bot = Bot(TG_TOKEN_DEV)
dp = Dispatcher()

images_list = []


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> Message:
    text_answer = f"Привет {message.from_user.first_name}"
    await message.answer(text_answer)


@dp.message(Command("image"))
async def give_photo(message: types.Message):
    for image_id in images_list:
        await message.answer_photo(photo=image_id)


@dp.message(F.photo)
async def get_photo(message: types.Message):
    image = message.photo[-1]
    images_list.append(image.file_id)

    await message.answer("Фото получено!")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
