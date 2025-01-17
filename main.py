import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import TOKEN
from handler import register_handlers
from scheduler import daily_progress

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def main():
    register_handlers(dp)
    asyncio.create_task(daily_progress(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
