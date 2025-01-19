import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv

from handler import register_handlers
from scheduler import daily_progress

logging.basicConfig(level=logging.INFO)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

storage = RedisStorage.from_url(REDIS_URL)

bot = Bot(token=BOT_TOKEN, storage=storage, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()


async def main():
    register_handlers(dp)
    asyncio.create_task(daily_progress(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
