import asyncio
import subprocess
import os
import json


from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from PIL import Image
from data import db_session
from typing import Optional

from config.config import TG_TOKEN_DEV
from data.user import User
from data.pattern import Pattern
from config.kb import (
    keyboard_user,
    keyboard_user_create_pattern,
    keyboard_user_pattern
)


__all__ = []


bot = Bot(TG_TOKEN_DEV)
dp = Dispatcher()

images_list = []
pattern_id = 0
pattern_folder = ""

users_in_support = []
in_time = []
in_answer = [False, 0]

flag_pattern_name = False
flag_view_pattern = False


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


def del_last_pattern(message):
    global flag_pattern_name
    if flag_pattern_name:
        flag_pattern_name = False
        patterns_user = DB_SESS.query(Pattern).filter(Pattern.user_id == message.from_user.id)
        last_pattern_id = max(i.pattern_id for i in patterns_user)
        last_pattern_user = DB_SESS.query(Pattern).filter(Pattern.pattern_id == last_pattern_id)
        for p in last_pattern_user:
            if not p.pattern_name:
                DB_SESS.delete(p)
        DB_SESS.commit()


def null_flags():
    global flag_view_pattern
    flag_view_pattern = False


def dir_cleaning(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Ошибка при удалении файла {filename}: {e}")


async def faceswap(patternfolder):
    dir_cleaning('/faceswap/inFace') # Очищаем папку с картинкой пользователя
    dir_cleaning('/faceswap/outDir') # Очищаем папку в которой лежат уже готовые фотки

    #код сохранения кортинки пользователя в папку faceswap/inFace

    subprocess.call("python faceswap/faceswap.py extract -i faceswap/inFace -o faceswap/faces -D mtcnn -A cv2-dnn",
                    shell=True) # Выполняем волшебные действия для добычи лица из фотки пользователя

    subprocess.call(f"python faceswap/faceswap.py convert -i faceswap/patterns/{patternfolder} -o faceswap/outDir -p faceswap/inFace/alignments.fsa -m faceswap/hackaton_smart_cnn -c color-transfer -M none -w opencv",
                    shell=True)# faceswap/patterns/название папки с шаблонами
    # В папке faceswap/outDir хранятся обработанные фотки


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> Message:
    del_last_pattern(message)
    null_flags()
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
    del_last_pattern(message)
    null_flags()
    await message.answer("Меню", reply_markup=keyboard_user)


# Команда для обращения в поддержку
@dp.message(Command("support"))
@dp.message(F.text == "Обратная связь")
async def support(message: types.Message):
    del_last_pattern(message)
    null_flags()
    if message.from_user.id in [i.id for i in DB_SESS.query(User).filter(User.is_developer).all()]:
        await message.reply("Вы являетесь админом и не можете задавать вопросы.")
    else:
        if message.from_user.id not in users_in_support:
            users_in_support.append(message.from_user.id)
        await message.reply("Введите ваше сообщение для поддержки.")


@dp.message(Command("generate"))
@dp.message(F.text == "Создать стикерпак")
async def create_stickerpak(message: types.Message) -> Message:
    del_last_pattern(message)
    null_flags()
    await message.answer(
        "Выбрать шаблон из доступных или создать свой?",
        reply_markup=keyboard_user_pattern,
    )


@dp.message(Command("new_pattern"))
@dp.message(F.text == "Создать шаблон")
async def create_template(message: types.Message) -> Message:
    del_last_pattern(message)
    null_flags()
    await message.answer(
        "Будет ли ваш шаблон доступен для других пользователей?\n"
        "Если да, для начала он должен будет пройти проверку администрацией,"
        " и только потом им смогут воспользоваться другие пользователи.",
        reply_markup=keyboard_user_create_pattern,
    )


@dp.message(Command("choose_pattern"))
@dp.message(F.text == "Выбрать шаблон")
async def choose_template(message: types.Message) -> Message:
    global flag_view_pattern
    flag_view_pattern = True
    base_patterns_collage = DB_SESS.query(Pattern).filter(Pattern.pattern_id == 0)
    media_group_goo = [
        InputMediaPhoto(media=i.image_id) for i in base_patterns_collage
    ]
    patterns = []
    for p in DB_SESS.query(Pattern).all():
        if p.pattern_name not in patterns and p.pattern_id in [1, 2]:
            patterns.append(p.pattern_name)
    kb_base_patterns = [
        [KeyboardButton(text=patterns[0])],
        [KeyboardButton(text=patterns[1])],
    ]
    await message.answer_media_group(media=media_group_goo)
    await message.answer(
        "Выберете нужный вам шаблон из предложенных или воспользуйтесь шаблонами "
        'других пользователей.\n/select_pattern "Название шаблона" - выбрать шаблон\n'
        "/patterns - вывести список всех доступных шаблонов\n"
        "Чтобы просмотреть шаблон, напишите в чат его название",
        reply_markup=ReplyKeyboardMarkup(keyboard=kb_base_patterns),
    )


@dp.message(Command("patterns"))
async def patterns(message: Message):
    base_patterns = []
    for p in range(len(DB_SESS.query(Pattern).filter(Pattern.pattern_id == 0).all())):
        base_patterns.append(DB_SESS.query(Pattern).filter(Pattern.pattern_id == (p + 1)).first().pattern_name)
    patterns_users = []
    for p in DB_SESS.query(Pattern).filter(Pattern.is_public == 1).all():
        if p.pattern_name not in patterns_users:
            patterns_users.append(p.pattern_name)
    my_patterns = []
    for p in DB_SESS.query(Pattern).filter(Pattern.user_id == message.from_user.id).all():
        if p.pattern_name not in my_patterns:
            my_patterns.append(p.pattern_name)
    await message.answer(f"Базовые шаблоны:\n{', '.join(base_patterns)}\n"
                         f"Шаблоны других пользователей:\n{', '.join(patterns_users)}\n"
                         f"Ваши шаблоны:\n{', '.join(my_patterns)}\n")


def create_folder_if_not_exists(folder_name):
    if not os.path.exists(f"faceswap/patterns/{folder_name}"):
        os.makedirs(f"faceswap/patterns/{folder_name}")


async def download_pattern(list_id, pattern_name):
    for i in list_id:
        image_info = await bot.get_file(i)
        image_path = image_info.file_path

        create_folder_if_not_exists(pattern_name)

        output_sticker_path = f"faceswap/patterns/{pattern_name}/{i}.png"

        await bot.download_file(image_path, output_sticker_path)

        with Image.open(output_sticker_path) as img:
            img.save(output_sticker_path)


async def download_image(image_id):
    image_info = await bot.get_file(image_id)
    image_path = image_info.file_path

    output_sticker_path = f"faceswap/inFace/{image_id}.png"

    await bot.download_file(image_path, output_sticker_path)

    with Image.open(output_sticker_path) as img:
        img.save(output_sticker_path)


@dp.message(Command("select_pattern"))
async def select_pattern(
        message: Message,
        command: CommandObject,
        state: FSMContext
):
    null_flags()
    del_last_pattern(message)

    global pattern_folder

    if command.args is None:
        await message.answer("Вы не написали название шаблона.")
    else:
        pattern_name = command.args
        pattern = DB_SESS.query(Pattern).filter(Pattern.pattern_name == pattern_name).all()
        if len(pattern) == 0:
            await message.answer("Шаблона с таким названием не существует")
        else:
            pattern_folder = pattern_name
            await message.answer(f"Шаблон {pattern_name} выбран, отправьте свою фотографию")
            await download_pattern([i.image_id for i in pattern], pattern_name)
            await state.set_state(PhotoState.waiting_for_photo)


# для генерации стикерпака
@dp.message(PhotoState.waiting_for_photo, F.photo)
async def process_message(
    message: types.Message,
    state: FSMContext,
) -> Message:
    image_id = message.photo[-1].file_id
    await download_image(image_id)
    # await faceswap(pattern_folder)
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
    null_flags()

    global pattern_id, flag_pattern_name

    patterns = DB_SESS.query(Pattern).all()
    if len(patterns) == 0:
        pattern_id = 0
    else:
        pattern_id = patterns[-1].pattern_id + 1
    await message.answer("Пришлите несколько фото для генерации шаблона.\n"
                         "Когда фото будет достаточно, напишите название шаблона в чат.")
    flag_pattern_name = True
    await state.set_state(PhotoState.waiting_for_photo2)


@dp.message(Command("for_me"))
@dp.message(F.text == "Приватный")
async def private_template(message: types.Message, state: FSMContext) -> Message:
    null_flags()

    global pattern_id, flag_pattern_name

    patterns = DB_SESS.query(Pattern).all()
    if len(patterns) == 0:
        pattern_id = 0
    else:
        pattern_id = patterns[-1].pattern_id + 1
    await message.answer("Пришлите несколько фото для генерации шаблона.\n"
                         "Когда фото будет достаточно, напишите название шаблона в чат.")
    flag_pattern_name = True
    await state.set_state(PhotoState.waiting_for_photo3)
# ---------------------------------------------------------------


# -------------------Адмиристратор---------------------------
@dp.message(Command("set_admin"))
async def set_admin(
        message: types.Message,
        command: CommandObject,
):
    if DB_SESS.query(User).filter(User.id == message.from_user.id).first().is_developer:
        if not command.args:
            await message.answer("Вы не ввели никнейм пользователя")
        U = DB_SESS.query(User).filter(User.tg_name == int(command.args)).first()
        U.is_developer = 1
        DB_SESS.commit()
        await message.answer(f"Пользователь {U.tg_name} назначен администратором")
    else:
        await message.answer(f"У вас нет прав, чтобы использовать эту команду")


@dp.message(Command("check_patterns"))
async def check_patterns(
        message: types.Message,
):
    if DB_SESS.query(User).filter(User.id == message.from_user.id).first().is_developer:
        patterns = []
        for i in DB_SESS.query(Pattern).filter(Pattern.for_everyone == 1 and Pattern.is_public != 1).all():
            if i.pattern_name not in patterns:
                patterns.append(i.pattern_name)
        await message.answer(f"Список шаблонов пользователей, нуждающихся в проверке:\n{', '.join(patterns)}")
    else:
        await message.answer(f"У вас нет прав, чтобы использовать эту команду")


@dp.message(Command("view_pattern"))
async def view_pattern(
        message: types.Message,
        command: CommandObject
):
    if DB_SESS.query(User).filter(User.id == message.from_user.id).first().is_developer:
        if command.args:
            pattern = DB_SESS.query(Pattern).filter(Pattern.pattern_name == command.args).all()
            if len(pattern) == 0:
                await message.answer("Шаблона с таким названием не существует или вы ввели неправильное название")
            else:
                media_group_goo = [
                    InputMediaPhoto(media=i.image_id) for i in pattern
                ]
                await message.answer_media_group(media=media_group_goo)
        else:
            await message.answer("Вы не указали название шаблона")
    else:
        await message.answer(f"У вас нет прав, чтобы использовать эту команду")


@dp.message(Command("approve_pattern"))
async def approve_pattern(
        message: types.Message,
        command: CommandObject
):
    if DB_SESS.query(User).filter(User.id == message.from_user.id).first().is_developer:
        if command.args:
            pattern = DB_SESS.query(Pattern).filter(Pattern.pattern_name == command.args).all()
            if len(pattern) == 0:
                await message.answer("Шаблона с таким названием не существует или вы ввели неправильное название")
            else:
                for i in pattern:
                    i.is_public = 1
                DB_SESS.commit()
                await message.answer(f"Шаблону {pattern[0].pattern_name} присвоен публичный статус")
        else:
            await message.answer("Вы не указали название ")
    else:
        await message.answer(f"У вас нет прав, чтобы использовать эту команду")


@dp.message(Command("not_approve_pattern"))
async def not_approve_pattern(
        message: types.Message,
        command: CommandObject
):
    if DB_SESS.query(User).filter(User.id == message.from_user.id).first().is_developer:
        if command.args:
            try:
                pattern_name, text = command.args.split(" ", maxsplit=1)
                print(pattern_name, text)
                pattern = DB_SESS.query(Pattern).filter(Pattern.pattern_name == pattern_name).all()
                if len(pattern) == 0:
                    await message.answer("Шаблона с таким названием не существует или вы ввели неправильное название")
                else:
                    for i in pattern:
                        i.for_everyone = 0
                    DB_SESS.commit()
                    await message.answer(f"Шаблону {pattern[0].pattern_name} присвоен публичный статус")
                # Если получилось меньше двух частей, вылетит ValueError
            except ValueError:
                await message.answer(
                    "Ошибка: неправильный формат команды. Пример:\n"
                    "/not_approve_pattern <Название шаблона> <Пояснение>"
                )
        else:
            await message.answer(f"Не переданы аргументы")
    else:
        await message.answer(f"У вас нет прав, чтобы использовать эту команду")


# --------------------------------------------------------------


# -------------------------Поддержка-----------------------------
@dp.message()
async def handle_message(message: types.Message):
    # Проверяем, обратился ли пользователь в поддержку
    global in_answer, flag_pattern_name, flag_view_pattern

    if flag_pattern_name:
        patterns_user = DB_SESS.query(Pattern).filter(Pattern.user_id == message.from_user.id).all()
        last_pattern_id = max(i.pattern_id for i in patterns_user)
        last_pattern_user = DB_SESS.query(Pattern).filter(Pattern.pattern_id == last_pattern_id).all()
        if message.text not in [i.pattern_name for i in DB_SESS.query(Pattern).all()]:
            for p in last_pattern_user:
                p.pattern_name = message.text
            DB_SESS.commit()
            flag_pattern_name = False
            await message.answer(f"Ваш шаблон был добавлен в базу данных с названием {message.text}")
        else:
            await message.answer(f"Шаблон с таким названием уже существует, придумайте другое.")
    elif flag_view_pattern:
        pattern_name = message.text
        pattern = DB_SESS.query(Pattern).filter(Pattern.pattern_name == pattern_name and
                                                (Pattern.is_public or Pattern.user_id == message.from_user.id)).all()
        if len(pattern) == 0:
            await message.answer("Шаблона с таким названием не существует")
        else:
            media_group_goo = [
                InputMediaPhoto(media=i.image_id) for i in pattern
            ]
            await message.answer_media_group(media=media_group_goo)
    elif in_answer[0]:
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
    with open('needSetup.json') as file:
        data = json.load(file)
    if data['needSetup']:    data['needSetup'] = 0
    with open('needSetup.json', 'w') as file:
        json.dump(data, file)
    subprocess.call("python faceswap/setup.py", shell=True)
    db_session.global_init("db/db.db")
    DB_SESS = db_session.create_session()
    asyncio.run(main())
