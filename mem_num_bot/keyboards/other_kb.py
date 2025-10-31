from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_kb():
    kb_list = [
        [KeyboardButton(text="✏️ Карточки")],
        [KeyboardButton(text="🧩 Мемори")],
        [KeyboardButton(text="❔ Справка")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def stop_fsm():
    kb_list = [
        [KeyboardButton(text="❌ Отмена")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Для того чтоб остановить создание '
        'нажми на одну из двух кнопок👇'
    )

def help_return():
    kb_list = [
                [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Вернуться в главное меню 👇'
    )