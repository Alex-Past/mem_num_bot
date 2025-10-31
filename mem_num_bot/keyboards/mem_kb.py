from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_mem_kb():
    kb_list = [
        [
         KeyboardButton(text="🧠 Экзамен"),
         KeyboardButton(text="💤 Пассивно")],
        [KeyboardButton(text="🏠 Главное меню"),]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )

