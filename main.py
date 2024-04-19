from aiogram import Bot, Dispatcher, types
from data import db_session

import asyncio


token = 'TOKEN'
bot = Bot(token)
dp = Dispatcher(bot)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    db_session.global_init("db/db.db")
    DB_SESS = db_session.create_session()
    asyncio.run(main())
