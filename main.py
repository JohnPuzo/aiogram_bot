import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handler import register_handlers
from scheduler import daily_progress
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)


load_dotenv()
bot = Bot(token=os.getenv('BOT_API'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def main():
    register_handlers(dp)
    asyncio.create_task(daily_progress(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
