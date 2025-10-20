from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_category_keyboard(categories):
    unique_category = [_ for _ in categories]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for category in unique_category:
        button = InlineKeyboardButton(
            text=category['category_name'],
            callback_data=f"category_id_{category['id']}"
        )
        keyboard.inline_keyboard.append([button])
    return keyboard


def generate_find_category_keyboard(categories):
    unique_category = [_ for _ in categories]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for category in unique_category:
        button = InlineKeyboardButton(
            text=category['category_name'],
            callback_data=f"category_name_{category['category_name']}"
        )
        keyboard.inline_keyboard.append([button])
    return keyboard


def main_note_kb():
    kb_list = [
        [KeyboardButton(text="📝 Добавить карточку"),
         KeyboardButton(text="📋 Просмотр карточек")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def find_note_kb():
    kb_list = [
        [KeyboardButton(text="📝 Категории")],
        [KeyboardButton(text="🔍 Поиск по тексту"),
         KeyboardButton(text="🔍 Поиск категории")],
        [KeyboardButton(text="📋 Список категорий"),
         KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите опцию👇"
    )


def rule_note_kb(note_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Изменить название", callback_data=f'edit_note_text_{note_id}')],
                         [InlineKeyboardButton(text="Изменить описание", callback_data=f'edit_desc_text_{note_id}')],
                         [InlineKeyboardButton(text="Удалить", callback_data=f'dell_note_{note_id}')]])


def rule_cat_kb(cat_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Изменить", callback_data=f'edit_cat_text_{cat_id}')],
                         [InlineKeyboardButton(text="Удалить", callback_data=f'dell_cat_{cat_id}')]])


def add_note_check():
    kb_list = [
        [KeyboardButton(text="✅ Все верно"), KeyboardButton(text="❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def del_check():
    kb_list = [
        [KeyboardButton(text="🗑 Удалить"), KeyboardButton(text="❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Подтвердите действие👇"
    )


def add_category_check():
    kb_list = [
        [KeyboardButton(text="✅ Добавить"), KeyboardButton(text="❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def main_category_kb():
    kb_list = [
        [KeyboardButton(text="📝 Добавить категорию"),
         KeyboardButton(text="📋 Список категорий")],
        [KeyboardButton(text="📋 Просмотр карточек"),
         KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Если подходящей категории нет, можешь ее создать👇"
    )


def all_category_kb():
    kb_list = [
        [KeyboardButton(text="📝 Добавить карточку"),
         KeyboardButton(text="📝 Добавить категорию")],
        [KeyboardButton(text="📋 Просмотр карточек"),
         KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Если подходящей категории нет, можешь ее создать👇"
    )
