import asyncio

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config.config import TG_TOKEN_DEV

__all__ = []


bot = Bot(TG_TOKEN_DEV)
dp = Dispatcher()

images_list = []


class PhotoState(StatesGroup):
    waiting_for_photo: State = State()


@dp.message(PhotoState.waiting_for_photo, F.photo)
async def process_message(
    message: types.Message,
    state: FSMContext,
) -> Message:
    image_id = message.photo[-1].file_id
    await message.answer_photo(photo=image_id)
    await state.clear()


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> Message:
    text_answer = f"Привет {message.from_user.first_name}"
    await message.answer(text_answer)


@dp.message(Command("image"))
async def get_photo(message: types.Message, state: FSMContext) -> Message:
    await message.answer("Пришлите своё фото")
    await state.set_state(PhotoState.waiting_for_photo)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
