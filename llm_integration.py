import os

from aiogram.fsm.context import FSMContext
from aiogram import types
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_gigachat.chat_models import GigaChat
from datafile import get_habit, get_style, get_user_progress

load_dotenv()

model = GigaChat(
    credentials=os.getenv("GIGACHAT_TOKEN"),
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False,
)

messages = {
    "global": """
Context: Ты профессиональный специалист по борьбе с вредными привычками. 
Ты будешь вести со мной диалог для борьба с моими вредными привычками, также будешь давать советы, 
как отвлечься от вредной привычки и напоминать почему я держусь уже много дней и почему мне нужно продолжить.
Диалог веди в {answer_style} форме
Вот моя привычка: {habit}
""",
    "advice": """
Context: Ты профессиональный специалист по борьбе с вредными привычками.
Дай мне ровно 1 совет, как отвлечься от моей привычки. В {answer_style} форме
Вот моя привычка: {habit}
""",
    "task": """
Context: Ты профессиональный специалист по борьбе с вредными привычками.
Дай мне ровно 1 короткое занятие, для отвлечения от моей вредной привычки. В {answer_style} форме
Вот моя привычка: {habit}
""",
    "reminder": """
Context: Ты профессиональный специалист по борьбе с вредными привычками
Напомни, почему я отказываюсь от вредной привычки уже {day_amount} дней? В {answer_style} форме
Вот моя привычка: {habit}
""",
}


async def preset_history(state: FSMContext, user_id, mode: str):
    global messages

    user_habit = await get_habit(user_id)
    habit = user_habit if user_habit else "Причина не указана, требуется уточнить у пользователя"

    user_style = await get_style(user_id)
    style = "формальной" if user_style else "неформальной"

    day_amount = await get_user_progress(user_id)

    history = []
    if mode == "global":
        context = messages["global"].format(answer_style=style, habit=habit)
    elif mode == "advice":
        context = messages["advice"].format(answer_style=style, habit=habit)
    elif mode == "task":
        context = messages["task"].format(answer_style=style, habit=habit)
    elif mode == "reminder":
        context = messages["reminder"].format(day_amount=day_amount, answer_style=style, habit=habit)
    else:
        raise ValueError("Invalid mode")

    history.append(SystemMessage(content=context))
    await state.update_data(history=history)


async def llm_invoke(message: types.Message, state: FSMContext, only_one_answer: bool):
    data = await state.get_data()
    history = data.get("history")

    if not only_one_answer:
        user_message = message.text.strip()
        human_message = HumanMessage(content=user_message)
        history.append(human_message)

    res = model.invoke(history)
    history.append(res)

    if only_one_answer:
        await state.update_data(history=[])

    return res.content