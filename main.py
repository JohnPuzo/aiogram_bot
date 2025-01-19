import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv

from datafile import create_dbs
from handler import router
from scheduler import daily_progress

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

storage = RedisStorage.from_url(REDIS_URL)

async def main():
    load_dotenv()

    await create_dbs()

    bot = Bot(token=BOT_TOKEN, storage=storage, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()
    dp.include_router(router)

    asyncio.create_task(daily_progress(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
