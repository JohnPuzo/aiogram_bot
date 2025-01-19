from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from datafile import *
from keyboard import main_menu, habit_keyboard, specialist_menu, type_keyboard
from llm_integration import llm_invoke, preset_history

router = Router()


class Form(StatesGroup):
    wait_custom_habit = State()
    friend_username = State()
    friend_username_del = State()
    llm_dialog = State()


default_habits = {
    "smoking": "Курение",
    "alcohol": "Алкоголь",
    "fastfood": "Фастфуд",
}

styles = {
    "true": "Серьезно",
    "false": "Шутливо",
}


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("Привет! Выбери привычку, от которой хочешь избавиться.", reply_markup=habit_keyboard)


@router.callback_query(lambda c: c.data.startswith("habit_"))
async def habit_selected(callback: types.CallbackQuery, state: FSMContext):
    habit = callback.data.split("_")[1]
    if habit == "custom":
        await callback.message.answer("Напиши свою привычку:")
        await state.set_state(Form.wait_custom_habit)
    else:
        await set_habit(callback.from_user.id, default_habits[habit])
        await callback.message.answer(f"Ты выбрал: {default_habits[habit]}.", reply_markup=main_menu)
        await callback.message.answer(
            "Теперь выбери, в какой форме ты хочешь получать советы: в шутливой или серьезной форме!",
            reply_markup=type_keyboard,
        )


@router.message(Form.wait_custom_habit)
async def process_custom_habit(message: types.Message, state: FSMContext):
    habit = message.text.strip()
    if await validate_habit_input(habit):
        await set_habit(message.from_user.id, habit)
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
async def style_selection(callback: types.CallbackQuery, state: FSMContext):
    style_str = callback.data.split("_")[1]
    style = True if style_str == "true" else False
    await set_style(callback.from_user.id, style)

    await callback.message.answer(f"Ты выбрал: {styles[style_str]}. Начнем борьбу! 💪", reply_markup=main_menu)


@router.message(F.text == "Мой прогресс")
async def show_progress(message: types.Message):
    user_id = message.from_user.id
    day = await get_user_progress(user_id)
    await message.answer(f"Ты не поддавался привычке {day} дней! 🎉")


@router.message(F.text == "Я сорвался")
async def stop_progress(message: types.Message):
    user_id = message.from_user.id
    await set_start_date(user_id)
    await message.answer("Не переживай, это случается! Ты должен попробовать снова. 😅")


@router.message(F.text == "Задание для отвлечения")
async def daily_task(message: types.Message, state: FSMContext):
    await preset_history(state=state, user_id=message.from_user.id, mode="task")
    result = await llm_invoke(message=message, state=state, only_one_answer=True)
    await message.answer(result)


@router.message(F.text == "Выбрать привычку")
async def change_habit(message: types.Message):
    await message.answer("Давай сменим привычку.", reply_markup=habit_keyboard)


@router.message(F.text == "Выбрать тип")
async def change_style(message: types.Message):
    await message.answer("Давай сменим тип!", reply_markup=type_keyboard)


@router.message(F.text == "Добавить друга")
async def cmd_add_friend(message: types.Message, state: FSMContext):
    await message.answer("Привет! Введите username друга (обычно начинается на @):")
    await state.set_state(Form.friend_username)


@router.message(Form.friend_username)
async def input_username_to_add(message: types.Message, state: FSMContext):
    username = message.text.strip().replace("@", "")

    if username == message.from_user.username:
        await message.answer("Ты не можешь добавить себя в друзья 🙃\n\nВведите имя друга!")
        return
    elif len(username) < 5 or len(username) > 32 or not all([i.isalnum() or i == "_" for i in username]):
        await message.answer("Имя пользователя должно быть длиной от 5 до 32 символов, а также может включать в себя только буквы, цифры и символ нижнего подчёркивания \'_\'")
        return
    if not await check_user_exists(username):
        await message.answer(f"Ваш друг с ником @{username} ещё не пользуется нашим ботом, либо вы допустили ошибку в нике.\n\nПопробуйте ввести ещё раз.")
        return

    user_id = message.from_user.id
    if await check_friend_exists(user_id, username):
        await message.answer(f"Друг с ником @{username} уже был в друзьях.")
        await state.clear()
        return

    await add_friend(user_id, username)
    await message.answer("Друг добавлен")
    await state.clear()


@router.message(F.text == "Удалить друга")
async def cmd_delete_friend(message: types.Message, state: FSMContext):
    await message.answer("Привет! Введите username друга (обычно начинается на @):")
    await state.set_state(Form.friend_username_del)


@router.message(Form.friend_username_del)
async def input_username_to_del(message: types.Message, state: FSMContext):
    username = message.text.strip().replace("@", "")

    if username == message.from_user.username:
        await message.answer("Введите имя друга, а не своё! 🙃")
        return
    elif len(username) < 5 or len(username) > 32 or not all([i.isalnum() or i == "_" for i in username]):
        await message.answer(
            "Имя пользователя должно быть длиной от 5 до 32 символов, а также может включать в себя только буквы, цифры и символ нижнего подчёркивания \'_\'")
        return

    user_id = message.from_user.id
    if not await check_friend_exists(user_id, username):
        await message.answer(f"Человека с ником @{username} не было в ваших друзьях.")
        await state.clear()
        return

    await delete_friend(user_id, username)
    await message.answer("Друг удалён")
    await state.clear()


@router.message(F.text == "Связаться со специалистом")
async def contact_specialist(message: types.Message, state: FSMContext):
    await message.answer("Опиши свою проблему. Специалист скоро ответит.", reply_markup=specialist_menu)
    await preset_history(state=state, user_id=message.from_user.id, mode="global")
    await state.set_state(Form.llm_dialog)


@router.message(Form.llm_dialog and F.text == "Назад в меню")
async def back_to_menu(message: types.Message, state: FSMContext):
    await message.answer("Возвращаю в главное меню.", reply_markup=main_menu)
    await state.clear()


@router.message(Form.llm_dialog)
async def llm_chat(message: types.Message, state: FSMContext):
    result = await llm_invoke(message=message, state=state, only_one_answer=False)
    await message.answer(result)


def register_handlers(dp):
    dp.include_router(router)


@router.message()
async def unknown_command(message: types.Message):
    await message.answer("Такой команды нет.")
