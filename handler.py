from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import middleware
from datafile import *
from keyboard import *
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
    "formal": "Формально 🎩",
    "informal": "Неформально 🤪",
}


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await add_user(message.from_user.id, message.from_user.username)
    await state.update_data(habit_selection_chain="True")
    await message.answer("Привет! Выбери привычку, от которой хочешь избавиться.", reply_markup=habit_keyboard)


@router.callback_query(lambda c: c.data.startswith("habit_"))
async def habit_selected(callback: types.CallbackQuery, state: FSMContext):
    habit = callback.data.split("_")[1]

    data = await state.get_data()
    try:
        flag = data["habit_selection_chain"]
    except KeyError:
        flag = "True"

    if habit == "custom":
        await callback.message.answer("Напиши свою привычку:")
        await state.set_state(Form.wait_custom_habit)
    else:
        await set_habit(callback.from_user.id, default_habits[habit])
        await callback.message.answer(f"Ты выбрал: {default_habits[habit]}.")
        if flag == "True":
            await callback.message.answer(
                "Теперь выбери, в какой форме ты хочешь получать советы: в шутливой или серьезной форме!",
                reply_markup=type_keyboard,
            )


@router.message(Form.wait_custom_habit)
async def process_custom_habit(message: types.Message, state: FSMContext):
    habit = message.text.strip()

    data = await state.get_data()
    try:
        flag = data["habit_selection_chain"]
    except KeyError:
        flag = "True"

    if await validate_habit_input(habit):
        await set_habit(message.from_user.id, habit)
        await message.answer(f"Ты выбрал: {habit}.")
        if flag == "True":
            await message.answer(
                "Теперь выбери, в какой форме ты хочешь получать советы: в шутливой или серьезной форме!",
                reply_markup=type_keyboard,
            )
        await state.clear()
    else:
        await message.answer(
            "Некорректный ввод. Привычка должна только буквы и пробелы. Слово должно быть написано в именительном падеже")


@router.callback_query(F.data.startswith("type_"))
@middleware.checking_habit
async def style_selection(callback: types.CallbackQuery, state: FSMContext):
    style_str = callback.data.split("_")[1]
    style = True if style_str == "formal" else False
    await set_style(callback.from_user.id, style)

    await callback.message.answer(f"Ты выбрал: {styles[style_str]}. Начнем борьбу! 💪", reply_markup=main_menu)

    await state.clear()


@router.message(Command("progress"))
@router.message(F.text == "Прогресс")
@middleware.checking_habit
@middleware.checking_style
async def show_progress_menu(message: types.Message):
    await message.answer("Выберите один из пунктов меню:", reply_markup=progress_menu)


@router.message(Command("gigachat"))
@router.message(F.text == "GigaChat")
@middleware.checking_habit
@middleware.checking_style
async def show_gigachat_menu(message: types.Message):
    await message.answer("Выберите один из пунктов меню:", reply_markup=gigachat_menu)


@router.message(Command("friends"))
@router.message(F.text == "Меню друзей")
@middleware.checking_habit
@middleware.checking_style
async def show_gigachat_menu(message: types.Message):
    await message.answer("Выберите один из пунктов меню:", reply_markup=friends_menu)


@router.message(Command("settings"))
@router.message(F.text == "Настройки")
@middleware.checking_habit
@middleware.checking_style
async def show_gigachat_menu(message: types.Message):
    await message.answer("Выберите один из пунктов меню:", reply_markup=change_menu)


@router.message(Command("menu"))
@router.message(F.text == "Назад")
@middleware.checking_habit
@middleware.checking_style
async def show_main_menu(message: types.Message):
    await message.answer("Выберите один из пунктов меню:", reply_markup=main_menu)


@router.message(Command("my_progress"))
@router.message(F.text == "Мой прогресс")
@middleware.checking_habit
@middleware.checking_style
async def show_progress(message: types.Message):
    user_id = message.from_user.id
    day = await get_user_progress(user_id)
    await message.answer(f"Ты не поддавался привычке {day} дней! 🎉")


@router.message(Command("stop_progress"))
@router.message(F.text == "Я сорвался")
@middleware.checking_habit
@middleware.checking_style
async def stop_progress(message: types.Message):
    user_id = message.from_user.id
    await set_start_date(user_id)
    await message.answer("Не переживай, это случается! Ты должен попробовать снова. 😅")


@router.message(Command("task"))
@router.message(F.text == "Задание для отвлечения")
@middleware.checking_habit
@middleware.checking_style
async def daily_task(message: types.Message, state: FSMContext):
    await preset_history(state=state, user_id=message.from_user.id, mode="task")
    result = await llm_invoke(message=message, state=state, only_one_answer=True)
    await message.answer(result)


@router.message(Command("change_habit"))
@router.message(F.text == "Выбрать привычку")
@middleware.checking_habit
@middleware.checking_style
async def change_habit(message: types.Message, state: FSMContext):
    await state.update_data(habit_selection_chain="False")
    await message.answer("Давай сменим привычку.", reply_markup=habit_keyboard)


@router.message(Command("change_style"))
@router.message(F.text == "Выбрать тип")
@middleware.checking_habit
@middleware.checking_style
async def change_style(message: types.Message):
    await message.answer("Давай сменим тип!", reply_markup=type_keyboard)


@router.message(Command("add_friend"))
@router.message(F.text == "Добавить друга")
@middleware.checking_habit
@middleware.checking_style
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


@router.message(Command("delete_friend"))
@router.message(F.text == "Удалить друга")
@middleware.checking_habit
@middleware.checking_style
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


@router.message(F.text == "Написать специалисту")
@middleware.checking_habit
@middleware.checking_style
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


@router.message()
@middleware.checking_habit
@middleware.checking_style
async def unknown_command(message: types.Message):
    await message.answer("Такой команды нет. Попробуйте что-нибудь из предложенных вариантов:", reply_markup=main_menu)


async def get_friends_progress(user_id):
    friends_ids = await get_friends_id_list(user_id)
    if not friends_ids:
        return []

    friends_progress = []
    for friend in friends_ids:
        friends_progress.append({
            "username": await get_username(friend),
            "habit": await get_habit(friend),
            "days": await get_user_progress(friend)
        })

    return friends_progress


async def daily_progress(bot):
    for user_id in await get_all_users():
        progress = await get_user_progress(user_id)
        friend_progress = await get_friends_progress(user_id)

        message = f"🌞 Добрый день! Твой прогресс: {progress} дней без привычки! 🚀"
        if len(friend_progress) > 0:
            message += "\n👬 **Прогресс твоих друзей:**\n"
            for friend in friend_progress:
                message += f"🔹 {friend['username']}: {friend['days']} дней (борется с {friend['habit']})\n"
        await bot.send_message(user_id, message)
