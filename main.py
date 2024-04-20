import asyncio

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from data import db_session

from config.config import TG_TOKEN_DEV
from data.user import User

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


def convert_to_binary_data(file):
    if file != '':
        with open(file, 'rb') as file:
            blob_data = file.read()
        return blob_data


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> Message:
    # developers = DB_SESS.query(User).filter(User.is_developer == True).all()
    # developers_workload = {i.id: i.workload for i in DB_SESS.query(User).filter(User.is_developer == True).all()}
    # print(developers_workload)

    if message.chat.id not in [i.id for i in DB_SESS.query(User).all()]:
        user = User(
            id=message.chat.id,
            full_name=message.from_user.full_name,
            tg_name=message.chat.username
        )
        DB_SESS.add(user)
        DB_SESS.commit()
    # print(message.from_user.id)
    text_answer = f"Привет {message.from_user.first_name}"
    await message.answer(text_answer)


@dp.message(Command("image"))
async def get_photo(message: types.Message, state: FSMContext) -> Message:
    await message.answer("Пришлите своё фото")
    await state.set_state(PhotoState.waiting_for_photo)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    db_session.global_init("db/db.db")
    DB_SESS = db_session.create_session()
    asyncio.run(main())
