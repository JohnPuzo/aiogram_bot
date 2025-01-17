from tkinter.tix import Form
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datafile import add_user, set_habit, set_type, validate_habit_input
from keyboard import main_menu, habit_keyboard, specialist_menu, type_keyboard
import pandas as pd
import json

DB_FILE = "users.csv"
router = Router()


class Form(StatesGroup):
    waiting_for_custom_habit = State()
    waiting_for_username = State()
    waiting_for_username_delete = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user(message.from_user.id, message.from_user.username)
    await message.answer("Привет! Выбери привычку, от которой хочешь избавиться.", reply_markup=habit_keyboard)



@router.callback_query(lambda c: c.data.startswith("habit_"))
async def habit_selected(callback: types.CallbackQuery, state: FSMContext):
    habit = callback.data.split("_")[1]
    if habit == "custom":
        await callback.message.answer("Напиши свою привычку:")
        await state.set_state(Form.waiting_for_custom_habit)
    else:
        set_habit(callback.from_user.id, habit)
        await callback.message.answer(f"Ты выбрал: {habit}.", reply_markup=main_menu)
        await callback.message.answer(
            "Теперь выбери, в какой форме ты хочешь получать советы: в шутливой или серьезной форме!",
            reply_markup=type_keyboard,
        )


@router.message(Form.waiting_for_custom_habit)
async def process_custom_habit(message: types.Message, state: FSMContext):
    habit = message.text
    if validate_habit_input(habit):
        set_habit(message.from_user.id, habit)
        await message.answer(f"Ты выбрал: {habit}.", reply_markup=main_menu)
        await message.answer(
            "Теперь выбери, в какой форме ты хочешь получать советы: в шутливой или серьезной форме!",
            reply_markup=type_keyboard,
        )
        await state.clear()
    else:
        await message.answer(
            "Некорректный ввод. Привычка должна быть от 3 до 30 символов и содержать только буквы и пробелы. " +
            "Слово должно быть написано в именительном падеже")


@router.callback_query(lambda c: c.data.startswith("type_"))
async def type_selected(callback: types.CallbackQuery):
    type = callback.data.split("_")[1]
    set_type(callback.from_user.id, type)
    await callback.message.answer(f"Ты выбрал: {type}. Начнем борьбу! 💪", reply_markup=main_menu)


@router.message(lambda msg: msg.text == "Мой прогресс")
async def show_progress(message: types.Message):
    user_id = message.from_user.id
    df = pd.read_csv(DB_FILE)
    day = df[df["user_id"] == user_id].iloc[0]["days"]
    await message.answer(f"Ты не поддавался привычке {day} дней! 🎉")


@router.message(lambda msg: msg.text == "Я сорвался")
async def show_progress(message: types.Message):
    await message.answer("Не переживай, это случается! Ты должен попробовать снова. 😅")
    user_id = message.from_user.id
    df = pd.read_csv(DB_FILE)
    df.loc[df["user_id"] == user_id, "days"] = 0
    df.to_csv(DB_FILE, index=False)


#здесь надо соотв добавить задание на отвлечение
@router.message(lambda msg: msg.text == "Задание для отвлечения")
async def daily_task(message: types.Message):
    await message.answer(f"Твоя задача: ты лох")


@router.message(lambda message: message.text == "Выбрать привычку")
async def change_habit(message: types.Message):
    await message.answer("Давай сменим привычку.", reply_markup=habit_keyboard)


@router.message(lambda message: message.text == "Выбрать тип")
async def change_type(message: types.Message):
    await message.answer("Давай сменим тип!", reply_markup=type_keyboard)


@router.message(lambda msg: msg.text == "Добавить друга")
async def add_friend(message: types.Message, state: FSMContext):
    await message.answer("Привет! Введите username пользователя, начиная с @:")
    await state.set_state(Form.waiting_for_username)


@router.message(Form.waiting_for_username)
async def input_username(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith('@'):
        await message.answer("Пожалуйста, введите username, начиная с @ (например, @username).")
        return
    df = pd.read_csv(DB_FILE)
    username = username[1:]
    if username not in df["username"].values:
        await message.answer(f"Не удалось найти пользователя с username {username}. Убедитесь, что username корректен.")
        return
    user_id = message.from_user.id
    user_row = df[df["user_id"] == user_id]
    friend_id = df[df["username"] == username].iloc[0]["user_id"]
    try:
        friends_list = json.loads(user_row.iloc[0]["friends"])
    except:
        friends_list = []
    if friend_id not in friends_list:
        friends_list.append(friend_id)
    else:
        await message.answer("Друг уже добавлен")
        return
    friends_list = [int(friend) for friend in friends_list]
    df.loc[df["user_id"] == user_id, "friends"] = json.dumps(friends_list)
    df.to_csv(DB_FILE, index=False)
    await message.answer("Друг добавлен")
    await state.clear()


@router.message(lambda msg: msg.text == "Удалить друга")
async def add_friend(message: types.Message, state: FSMContext):
    await message.answer("Привет! Введите username пользователя, начиная с @:")
    await state.set_state(Form.waiting_for_username_delete)


@router.message(Form.waiting_for_username_delete)
async def input_username(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith('@'):
        await message.answer("Пожалуйста, введите username, начиная с @ (например, @username).")
        return
    df = pd.read_csv(DB_FILE)
    username = username[1:]
    if username not in df["username"].values:
        await message.answer(f"Не удалось найти пользователя с username {username}. Убедитесь, что username корректен.")
        return
    user_id = message.from_user.id
    user_row = df[df["user_id"] == user_id]
    friend_id = df[df["username"] == username].iloc[0]["user_id"]
    try:
        friends_list = json.loads(user_row.iloc[0]["friends"])
    except:
        friends_list = []
    if friend_id not in friends_list:
        await message.answer("Друг уже удален")
        return
    else:
        friends_list.remove(friend_id)
    friends_list = [int(friend) for friend in friends_list]
    df.loc[df["user_id"] == user_id, "friends"] = json.dumps(friends_list)
    df.to_csv(DB_FILE, index=False)
    await message.answer("Друг удален")
    await state.clear()


# здесь соотв связь со специалистом
@router.message(lambda msg: msg.text == "Связаться со специалистом")
async def contact_specialist(message: types.Message):
    await message.answer("Опиши свою проблему. Специалист скоро ответит.", reply_markup=specialist_menu)


@router.message(lambda msg: msg.text == "Назад в меню")
async def back_to_menu(message: types.Message):
    await message.answer("Возвращаю в главное меню.", reply_markup=main_menu)


def register_handlers(dp):
    dp.include_router(router)


@router.message()
async def unknown_command(message: types.Message):
    await message.answer("Такой команды нет.")
