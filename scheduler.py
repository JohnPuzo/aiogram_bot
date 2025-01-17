import asyncio
import json

from aiogram import Bot
import pandas as pd
from datetime import datetime, timedelta

DB_FILE = "users.csv"

#сюда надо добавить ежедневную причину
def get_progress(user_id: int):
    df = pd.read_csv(DB_FILE)
    user = df[df["user_id"] == user_id]
    if not user.empty:
        return user.iloc[0]["days"]
    return 0


def get_friend_progress(user_id: int):
    df = pd.read_csv(DB_FILE)
    user = df[df["user_id"] == user_id]
    if user.empty:
        return []
    try:
        friends_list = json.loads(user.iloc[0]["friends"])
    except:
        return None
    friends_progress = []

    for friend_id in friends_list:
        friend = df[df["user_id"] == friend_id]
        friends_progress.append({
            "username": friend.iloc[0]["username"],
            "habit": friend.iloc[0]["habit"],
            "days": friend.iloc[0]["days"]
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

        df = pd.read_csv(DB_FILE)
        for _, row in df.iterrows():
            user_id = int(row["user_id"])
            progress = get_progress(user_id)
            friend_progress = get_friend_progress(user_id)

            message = f"🌞 Добрый день! Твой прогресс: {progress} дней без привычки! 🚀"
            if friend_progress is not None:
                message += "\n👬 **Прогресс твоих друзей:**\n"
                for friend in friend_progress:
                    message += f"🔹 {friend['username']}: {friend['days']} дней (борется с {friend['habit']})\n"
            await bot.send_message(user_id, message)
        df = pd.read_csv(DB_FILE)
        df["days"] = df["days"] + 1
        df.to_csv(DB_FILE, index=False)
        await asyncio.sleep(86400 - 60)
