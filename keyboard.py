from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мой прогресс"), KeyboardButton(text="Задание для отвлечения"), KeyboardButton(text="Связаться со специалистом")],
        [KeyboardButton(text="Выбрать привычку"), KeyboardButton(text="Я сорвался"), KeyboardButton(text="Выбрать тип")],
        [KeyboardButton(text="Добавить друга"), KeyboardButton(text="Удалить друга")]
    ],
    resize_keyboard=True
)


habit_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Курение 🚬", callback_data="habit_smoking")],
        [InlineKeyboardButton(text="Алкоголь 🍷", callback_data="habit_alcohol")],
        [InlineKeyboardButton(text="Фастфуд 🍔", callback_data="habit_fastfood")],
        [InlineKeyboardButton(text="Своя привычка ✍", callback_data="habit_custom")]
    ]
)

type_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Серьезно 😎", callback_data="type_true")],
        [InlineKeyboardButton(text="Шутливо 😂", callback_data="type_false")],
    ]
)

specialist_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад в меню")]
    ],
    resize_keyboard=True
)
