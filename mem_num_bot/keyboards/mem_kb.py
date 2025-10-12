from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_mem_kb():
    kb_list = [
        [KeyboardButton(text="🎲 Случайная карточка"),
         KeyboardButton(text="Экзамен")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def create_random_card_keyboard():
    """Клавиатура для случайной карточки."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🃏 Показать полностью", callback_data="show_full_random_note")],
        # [InlineKeyboardButton(text="🎲 Другая карточка", callback_data="another_random_card")]
    ])
    return keyboard