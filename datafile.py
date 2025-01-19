import logging
import os
import re
from datetime import date

import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def get_db_connection():
    try:
        hostname = os.getenv('DB_HOST')
        username = os.getenv('DB_USER')
        database = os.getenv('DB_NAME')

        if not all([hostname, username, database]):
            raise ValueError("Missing environment variables")

        return await asyncpg.connect(host=hostname, user=username, database=database)
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        return None


async def add_user(user_id, username):
    conn = await get_db_connection()
    if not conn:
        return None

    async with conn.transaction():
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                _id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL UNIQUE,
                username VARCHAR(255),
                habit VARCHAR(255),
                start_date DATE,
                communication_style BOOLEAN DEFAULT TRUE
            );
        """)

        query = """
            INSERT INTO users (user_id, username)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
            SET username = $2;
        """

        await conn.execute(query, str(user_id), username)


async def get_all_users():
    conn = await get_db_connection()
    if not conn:
        return None

    users = [user[0] for user in await conn.fetch("SELECT user_id FROM users")]
    return users if users else None


async def get_username(user_id):
    conn = await get_db_connection()
    if not conn:
        return None

    name = await conn.fetchrow("SELECT username FROM users WHERE user_id = $1", str(user_id))
    return name[0] if name else None


async def get_habit(user_id):
    conn = await get_db_connection()
    if not conn:
        return None

    habit = await conn.fetchrow("SELECT habit FROM users WHERE user_id = $1", str(user_id))
    return habit[0] if habit else None


async def set_habit(user_id, habit):
    conn = await get_db_connection()
    if not conn:
        return None

    async with conn.transaction():
        query = """
            UPDATE users
            SET habit = $1, start_date = $2
            WHERE user_id = $3;
        """

        await conn.execute(query, habit, date.today(), str(user_id))


async def get_style(user_id):
    conn = await get_db_connection()
    if not conn:
        return None

    style = await conn.fetchrow("SELECT communication_style FROM users WHERE user_id = $1", str(user_id))
    return style[0] if style else None


async def set_style(user_id, style: bool):
    conn = await get_db_connection()
    if not conn:
        return None

    async with conn.transaction():
        query = """
            UPDATE users
            SET communication_style = $1
            WHERE user_id = $2;
        """

        await conn.execute(query, style, str(user_id))


async def get_user_progress(user_id):
    conn = await get_db_connection()
    if not conn:
        return None

    start_date = await conn.fetchrow("SELECT start_date FROM users WHERE user_id = $1", str(user_id))
    days_passed = (date.today() - start_date[0]).days
    return days_passed


async def set_start_date(user_id):
    conn = await get_db_connection()
    if not conn:
        return None

    async with conn.transaction():
        await conn.execute("UPDATE users SET start_date = $1 WHERE user_id = $2", date.today(), str(user_id))


async def check_table_exists(table_name):
    conn = await get_db_connection()
    if not conn:
        return None

    query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = $1
            );
        """
    result = await conn.fetchrow(query, table_name)

    if result[0]:
        return True
    return False


async def check_user_exists(username):
    conn = await get_db_connection()
    if not conn:
        return None

    user = await conn.fetchrow("SELECT user_id FROM users WHERE username = $1", username)
    return user is not None


async def check_friend_exists(user_id, friend_username):
    conn = await get_db_connection()
    if not conn:
        return None

    result = await conn.fetchrow("SELECT user_id FROM users WHERE username = $1", friend_username)
    friend_id = result['user_id'] if result else None
    if not friend_id:
        return False

    if await check_table_exists('friends'):
        query = """
            SELECT COUNT(*) 
            FROM friends
            WHERE user_id = $1 AND friend_id = $2;
        """

        result = await conn.fetchrow(query, str(user_id), friend_id)
        return result[0] > 0
    else:
        return False


async def add_friend(user_id, friend_username):
    conn = await get_db_connection()
    if not conn:
        return None

    async with conn.transaction():
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS friends(
                user_id VARCHAR(255) REFERENCES users(user_id) ON DELETE CASCADE,
                friend_id VARCHAR(255) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE (user_id, friend_id)
            );
        """)

        query = """
            INSERT INTO friends (user_id, friend_id)
            VALUES ($1, (SELECT user_id FROM users WHERE username = $2))
            ON CONFLICT (user_id, friend_id) DO NOTHING
            """
        await conn.execute(query, str(user_id), friend_username)

        query = """
            INSERT INTO friends (user_id, friend_id)
            VALUES ((SELECT user_id FROM users WHERE username = $2), $1)
            ON CONFLICT (user_id, friend_id) DO NOTHING;
        """
        await conn.execute(query, str(user_id), friend_username)


async def delete_friend(user_id, friend_username):
    conn = await get_db_connection()
    if not conn:
        return None

    async with conn.transaction():
        if await check_table_exists('friends'):
            query = """
                    DELETE FROM friends
                    WHERE user_id = $1 AND friend_id = (SELECT user_id FROM users WHERE username = $2);
                    """
            await conn.execute(query, str(user_id), friend_username)

            query = """
                    DELETE FROM friends
                    WHERE user_id = (SELECT user_id FROM users WHERE username = $2) AND friend_id = $1;
                """
            await conn.execute(query, str(user_id), friend_username)


async def get_friends_id_list(user_id):
    conn = await get_db_connection()
    if not conn:
        return None

    if not await check_table_exists('friends'):
        return None

    result = await conn.fetch("SELECT friend_id FROM friends WHERE user_id = $1", str(user_id))
    friend_list = [friend[0] for friend in result]

    return friend_list


async def validate_habit_input(habit: str) -> bool:
    if len(habit) < 3 or len(habit) > 30 or not re.match(r"^[a-zA-Zа-яА-Я \s]+$", habit):
        return False
    return True
