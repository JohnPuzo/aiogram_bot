from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Прогресс"), KeyboardButton(text="GigaChat")],
        [KeyboardButton(text="Меню друзей"), KeyboardButton(text="Настройки")],
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
        [InlineKeyboardButton(text="Формально 🎩", callback_data="type_formal")],
        [InlineKeyboardButton(text="Неформально 🤪", callback_data="type_informal")],
    ]
)

specialist_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад в меню")]
    ],
    resize_keyboard=True
)

progress_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мой прогресс"), KeyboardButton(text="Я сорвался")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True
)

gigachat_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Задание для отвлечения"), KeyboardButton(text="Написать специалисту")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True
)

friends_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить друга"), KeyboardButton(text="Удалить друга")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True
)

change_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выбрать привычку"), KeyboardButton(text="Выбрать тип")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True
)