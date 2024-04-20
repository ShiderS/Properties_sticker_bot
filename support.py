# import asyncio
# import logging
# from typing import Optional
#
# import aiogram
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters.callback_data import CallbackData
# from aiogram.filters.command import Command
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram import F
# from aiogram.utils.keyboard import InlineKeyboardBuilder
#
# #await message.reply("Ваше сообщение было передано администратору. Ожидайте ответа.")
# # if message.from_user.id == ADMIN_ID:
# #     await message.reply("Вы являетесь админом и не можете задавать вопросы.")
# # Установка уровня логгирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# logging.basicConfig(level=logging.INFO)
#
# # Указываем токен вашего бота
# BOT_TOKEN = '5731308348:AAHAYI-eMow-FrO83L3949QQyaZOS9wAK0Y'
#
#
# # Инициализация бота и диспетчера
# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher()


from aiogram.filters.callback_data import CallbackData
from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder



ADMIN_ID = 997029220
users_in_support = []
in_time = []
in_answer = [False, 0]


class DataForAnswer(CallbackData, prefix="fabnum"):
    action: str
    id: Optional[int] = None


def markup_for_admin_ans(user_id):
    anser_admin_kb = InlineKeyboardBuilder()
    anser_admin_kb.button(text='Ответить', callback_data=DataForAnswer(action="ok", id=user_id))
    anser_admin_kb.button(text='Завершить диалог', callback_data=DataForAnswer(action="cancel", id=user_id))
    anser_admin_kb.adjust(2)
    return anser_admin_kb


# Команда для обращения в поддержку
@dp.message(Command('support'))
async def support(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("Вы являетесь админом и не можете задавать вопросы.")
    else:
        if message.from_user.id not in users_in_support:
            users_in_support.append(message.from_user.id)
        await message.reply("Введите ваше сообщение для поддержки.")


@dp.message()
async def handle_message(message: types.Message):
    # Проверяем, обратился ли пользователь в поддержку
    global in_answer
    if in_answer[0]:
        await bot.send_message(in_answer[1], message.text)
        await message.reply("Ответ отправлен пользователю")
        users_in_support.remove(in_answer[1])
        in_time.remove(in_answer[1])
        in_answer = [False, 0]
    elif message.from_user.id in users_in_support and message.from_user.id not in in_time:
        ##################
        admin_message = f"Пользователь {message.from_user.first_name} задал вопрос: {message.text}"
        await bot.send_message(ADMIN_ID, admin_message, reply_markup=markup_for_admin_ans(message.from_user.id).as_markup())
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
        await bot.send_message(callback_data.id, "Вопрос отклонён")
        await callback.message.edit_text(f"Вопрос отклонён")
        users_in_support.remove(callback_data.id)
        in_time.remove(callback_data.id)
    await callback.answer()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


