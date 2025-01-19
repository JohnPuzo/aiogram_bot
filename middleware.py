from functools import wraps

from aiogram.types import CallbackQuery, Message

from datafile import get_habit, get_style


def checking_habit(handler):
    @wraps(handler)
    async def wrapper(*args, **kwargs):
        user_id = None

        if isinstance(args[0], CallbackQuery) or isinstance(args[0], Message):
            user_id = args[0].from_user.id

        if user_id is not None and await get_habit(user_id) is not None:
            return await handler(*args, **kwargs)
        else:
            if isinstance(args[0], CallbackQuery):
                await args[0].message.answer("Для начала необходимо пройти регистрацию. Нажмите на /start, укажите свою привычку, а также стиль общения")
            elif isinstance(args[0], Message):
                await args[0].answer("Для начала необходимо пройти регистрацию. Нажмите на /start, укажите свою привычку, а также стиль общения")
            return

    return wrapper


def checking_style(handler):
    @wraps(handler)
    async def wrapper(*args, **kwargs):
        user_id = None

        if isinstance(args[0], CallbackQuery) or isinstance(args[0], Message):
            user_id = args[0].from_user.id

        if user_id is not None and await get_style(user_id) is not None:
            return await handler(*args, **kwargs)
        else:
            if isinstance(args[0], CallbackQuery):
                await args[0].message.answer("Для начала необходимо пройти регистрацию. Нажмите на /start, укажите свою привычку, а также стиль общения")
            elif isinstance(args[0], Message):
                await args[0].answer("Для начала необходимо пройти регистрацию. Нажмите на /start, укажите свою привычку, а также стиль общения")
            return

    return wrapper