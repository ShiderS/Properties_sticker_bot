import asyncio


from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config.config import TG_TOKEN_DEV
from config.kb import (
    keyboard_user,
    keyboard_user_create_pattern,
    keyboard_user_pattern,
)


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
async def start(message: types.Message) -> Message:
    text_answer = f"Привет {message.from_user.first_name}!"
    await message.answer(text_answer, reply_markup=keyboard_user)


@dp.message(Command("help"))
@dp.message(F.text == "Помощь")
async def help(message: types.Message) -> Message:
    await message.answer("Выбрать шаблон")


@dp.message(Command("menu"))
@dp.message(F.text == "Меню")
async def menu(message: types.Message) -> Message:
    await message.answer("Меню", reply_markup=keyboard_user)


@dp.message(Command("image"))
async def get_photo(message: types.Message, state: FSMContext) -> Message:
    await message.answer("Пришлите своё фото")
    await state.set_state(PhotoState.waiting_for_photo)


@dp.message(Command("support"))
@dp.message(F.text == "Обратная связь")
async def feedback(message: types.Message) -> Message:
    await message.answer("Обратная связь")


@dp.message(Command("generate"))
@dp.message(F.text == "Создать стикерпак")
async def create_stickerpak(message: types.Message) -> Message:
    await message.answer(
        "Создать стикерпак",
        reply_markup=keyboard_user_pattern,
    )


@dp.message(Command("new_pattern"))
@dp.message(F.text == "Создать шаблон")
async def create_template(message: types.Message) -> Message:
    await message.answer(
        "Выбрать шаблон",
        reply_markup=keyboard_user_create_pattern,
    )


@dp.message(Command("choose_pattern"))
@dp.message(F.text == "Выбрать шаблон")
async def choose_template(message: types.Message) -> Message:
    await message.answer("Выбрать шаблон")


@dp.message(Command("for_everyone"))
@dp.message(F.text == "Публичный")
async def public_template(message: types.Message) -> Message:
    await message.answer("Публичный")


@dp.message(Command("for_me"))
@dp.message(F.text == "Приватный")
async def private_template(message: types.Message) -> Message:
    await message.answer("Приватный")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
