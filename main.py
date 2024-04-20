import asyncio


from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.types.input_media_photo import InputMediaPhoto
from data import db_session
from typing import Optional

from config.config import TG_TOKEN_DEV
from data.user import User
from data.pattern import Pattern
from config.kb import (
    keyboard_user,
    keyboard_user_create_pattern,
    keyboard_user_pattern,
)


__all__ = []


bot = Bot(TG_TOKEN_DEV)
dp = Dispatcher()

images_list = []
pattern_id = 0

users_in_support = []
in_time = []
in_answer = [False, 0]


class PhotoState(StatesGroup):
    waiting_for_photo: State = State()
    waiting_for_photo2: State = State()
    waiting_for_photo3: State = State()


class DataForAnswer(CallbackData, prefix="fabnum"):
    action: str
    id: Optional[int] = None


def markup_for_admin_ans(user_id):
    anser_admin_kb = InlineKeyboardBuilder()
    anser_admin_kb.button(text='Ответить', callback_data=DataForAnswer(action="ok", id=user_id))
    anser_admin_kb.button(text='Завершить диалог', callback_data=DataForAnswer(action="cancel", id=user_id))
    anser_admin_kb.adjust(2)
    return anser_admin_kb


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> Message:
    if message.chat.id not in [i.id for i in DB_SESS.query(User).all()]:
        user = User(
            id=message.chat.id,
            full_name=message.from_user.full_name,
            tg_name=message.chat.username
        )
        DB_SESS.add(user)
        DB_SESS.commit()
    text_answer = f"Привет {message.from_user.first_name}"
    await message.answer(text_answer, reply_markup=keyboard_user)


@dp.message(Command("help"))
@dp.message(F.text == "Помощь")
async def help(message: types.Message) -> Message:
    await message.answer("Помощь")


@dp.message(Command("menu"))
@dp.message(F.text == "Меню")
async def menu(message: types.Message) -> Message:
    await message.answer("Меню", reply_markup=keyboard_user)


@dp.message(Command("image"))
async def get_photo(message: types.Message, state: FSMContext) -> Message:
    await message.answer("Пришлите своё фото")
    await state.set_state(PhotoState.waiting_for_photo)


# Команда для обращения в поддержку
@dp.message(Command("support"))
@dp.message(F.text == "Обратная связь")
async def support(message: types.Message):
    if message.from_user.id in [i.id for i in DB_SESS.query(User).filter(User.is_developer).all()]:
        await message.reply("Вы являетесь админом и не можете задавать вопросы.")
    else:
        if message.from_user.id not in users_in_support:
            users_in_support.append(message.from_user.id)
        await message.reply("Введите ваше сообщение для поддержки.")


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
        "Создать шаблон",
        reply_markup=keyboard_user_create_pattern,
    )


@dp.message(Command("choose_pattern"))
@dp.message(F.text == "Выбрать шаблон")
async def choose_template(message: types.Message) -> Message:
    await message.answer("Выбрать шаблон")


# для генерации стикерпака
@dp.message(PhotoState.waiting_for_photo, F.photo)
async def process_message(
    message: types.Message,
    state: FSMContext,
) -> Message:
    image_id = message.photo[-1].file_id
    await message.answer_photo(photo=image_id)
    await state.clear()


# ----------------------Генерация шаблонов-------------------------
# для генерации публичного шаблона
@dp.message(PhotoState.waiting_for_photo2, F.photo)
async def process_message(
    message: types.Message,
    state: FSMContext,
) -> Message:
    global pattern_id

    image_id = message.photo[-1].file_id

    await create_pattern_db(pattern_id, message.from_user.id, True, image_id)
    await state.clear()


# для генерации приватного шалона
@dp.message(PhotoState.waiting_for_photo3, F.photo)
async def process_message(
    message: types.Message,
    state: FSMContext,
) -> Message:
    global pattern_id

    image_id = message.photo[-1].file_id

    await create_pattern_db(pattern_id, message.from_user.id, False, image_id)
    await state.clear()


# занесение шаблона в базу данных
async def create_pattern_db(pattern_id, user_id, for_everyone, file_id):
    pattern = Pattern(
        pattern_id=pattern_id,
        user_id=user_id,
        for_everyone=for_everyone,
        image_id=file_id
    )
    DB_SESS.add(pattern)
    DB_SESS.commit()


@dp.message(Command("for_everyone"))
@dp.message(F.text == "Публичный")
async def public_template(message: types.Message, state: FSMContext) -> Message:
    global pattern_id
    patterns = DB_SESS.query(Pattern).all()
    if len(patterns) == 0:
        pattern_id = 0
    else:
        pattern_id = patterns[-1].pattern_id + 1
    await message.answer("Пришлите несколько фото для генерации шаблона(обязательно одним сообщением)")
    await state.set_state(PhotoState.waiting_for_photo2)


@dp.message(Command("for_me"))
@dp.message(F.text == "Приватный")
async def private_template(message: types.Message, state: FSMContext) -> Message:
    global pattern_id
    patterns = DB_SESS.query(Pattern).all()
    if len(patterns) == 0:
        pattern_id = 0
    else:
        pattern_id = patterns[-1].pattern_id + 1
    await message.answer("Пришлите несколько фото для генерации шаблона(обязательно одним сообщением)")
    await state.set_state(PhotoState.waiting_for_photo3)
# ---------------------------------------------------------------


# -------------------------Поддержка-----------------------------
@dp.message()
async def handle_message(message: types.Message):
    # Проверяем, обратился ли пользователь в поддержку
    global in_answer
    if in_answer[0]:
        admin = DB_SESS.query(User).filter(User.id == message.from_user.id).first()
        admin.workload -= 1
        DB_SESS.commit()
        await bot.send_message(in_answer[1], message.text)
        await message.reply("Ответ отправлен пользователю")
        users_in_support.remove(in_answer[1])
        in_time.remove(in_answer[1])
        in_answer = [False, 0]
    elif message.from_user.id in users_in_support and message.from_user.id not in in_time:
        ##################
        developer_id = sorted(
            {i.id: i.workload for i in DB_SESS.query(User).filter(User.is_developer).all()}.items(),
            key=lambda x: x[1])[0][0]
        admin = DB_SESS.query(User).filter(User.id == developer_id).first()
        admin.workload += 1
        DB_SESS.commit()
        admin_message = f"Пользователь {message.from_user.first_name} задал вопрос: {message.text}"
        await bot.send_message(developer_id, admin_message, reply_markup=markup_for_admin_ans(message.from_user.id).as_markup())
        in_time.append(message.from_user.id)
        ##################
        await message.reply("Ваше сообщение было передано администратору. Ожидайте ответа.")
    elif message.from_user.id in in_time:
        await message.reply("Ваше сообщение было передано администратору. Ожидайте ответа.")
    else:
        await message.reply("Простите, я не понимаю вашего сообщения.")


@dp.callback_query(DataForAnswer.filter())
async def callbacks_num_change_fab(callback: types.CallbackQuery, callback_data: DataForAnswer):
    global in_answer
    if callback_data.action == "ok":
        await callback.message.edit_text(f"Напишите текст для ответа:")
        in_answer = [True, callback_data.id]

    elif callback_data.action == "cancel":
        admin = DB_SESS.query(User).filter(User.id == callback_data.id).first()
        admin.workload -= 1
        DB_SESS.commit()
        await bot.send_message(callback_data.id, "Вопрос отклонён")
        await callback.message.edit_text(f"Вопрос отклонён")
        users_in_support.remove(callback_data.id)
        in_time.remove(callback_data.id)
    await callback.answer()
# -----------------------------------------------------------------------------


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    db_session.global_init("db/db.db")
    DB_SESS = db_session.create_session()
    asyncio.run(main())
