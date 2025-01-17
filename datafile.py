import re
import pandas as pd
import os

DB_FILE = "users.csv"


def add_user(user_id, username):
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["user_id", "username", "habit", "days", "friends", "type"])
    else:
        df = pd.read_csv(DB_FILE)
    if user_id not in df["user_id"].values:
        new_user = pd.DataFrame(
            {"user_id": user_id, "username": username, "habit": "", "days": 0, "friends": "[]", "type": ""}, index=[0])
        df = df._append(new_user, ignore_index=True)
        df.to_csv(DB_FILE, index=False)


def set_habit(user_id, habit):
    df = pd.read_csv(DB_FILE)
    df.loc[df["user_id"] == user_id, "habit"] = habit
    df.to_csv(DB_FILE, index=False)


def set_type(user_id, type):
    df = pd.read_csv(DB_FILE)
    df.loc[df["user_id"] == user_id, "type"] = type
    df.to_csv(DB_FILE, index=False)


def validate_habit_input(habit: str) -> bool:
    if len(habit) < 3 or len(habit) > 15 or not re.match(r"^[a-zA-Zа-яА-Я\s]+$", habit):
        return False
    return True