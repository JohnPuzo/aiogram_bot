import asyncio

from aiogram import Bot
from datetime import datetime, timedelta

from datafile import *


async def get_friends_progress(user_id):
    friends_ids = await get_friends_id_list(user_id)
    if not friends_ids:
        return None

    friends_progress = []
    for friend in friends_ids:
        friends_progress.append({
            "username": await get_username(friend),
            "habit": await get_habit(friend),
            "days": await get_user_progress(friend)
        })

    return friends_progress


async def wait_until_noon():
    now = datetime.now()
    noon = now.replace(hour=12, minute=0, second=0, microsecond=0)

    if now > noon:
        noon += timedelta(days=1)

    wait_time = (noon - now).total_seconds()
    await asyncio.sleep(wait_time)


async def daily_progress(bot: Bot):
    while True:
        await wait_until_noon()

        for user_id in await get_all_users():
            progress = await get_user_progress(user_id)
            friend_progress = await get_friends_progress(user_id)

            message = f"🌞 Добрый день! Твой прогресс: {progress} дней без привычки! 🚀"
            if friend_progress is not None:
                message += "\n👬 **Прогресс твоих друзей:**\n"
                for friend in friend_progress:
                    message += f"🔹 {friend['username']}: {friend['days']} дней (борется с {friend['habit']})\n"
            await bot.send_message(user_id, message)

        await asyncio.sleep(86400 - 60)
