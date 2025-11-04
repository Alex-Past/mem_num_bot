from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def admin_main_kb():
    kb_list = [
        [KeyboardButton(text="Рассылка"),
         KeyboardButton(text="Пользователи")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )

