from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)


def create_categories_keyboard(categories, selected_categories=None):
    """Клавиатура для выбора категорий экзамена."""
    if selected_categories is None:
        selected_categories = []
    
    keyboard = []
    
    # Кнопки категорий
    for category in categories:
        is_selected = category['id'] in selected_categories
        emoji = "✅" if is_selected else "⚪️"
        text = f"{emoji} {category['category_name']}"
        keyboard.append([
            InlineKeyboardButton(
                text=text, 
                callback_data=f"exam_category_{category['id']}"
            )
        ])
    
    # Кнопки управления
    keyboard.append([
        InlineKeyboardButton(text="🎯 Все категории", callback_data="exam_category_all")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🚀 Начать экзамен", callback_data="start_exam")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_exam_main_keyboard(has_difficult_notes: bool = False):
    """Основная клавиатура экзамена с кнопкой сложных карточек."""
    keyboard = [
        [InlineKeyboardButton(text="📚 Выбрать категории", callback_data="select_categories")],
    ]
    
    if has_difficult_notes:
        keyboard.append([
            InlineKeyboardButton(text="🎯 Повторить сложные", callback_data="difficult_notes")
        ])
    
    # keyboard.append([
    #     InlineKeyboardButton(text="🔄 Случайные все", callback_data="random_all")
    # ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_exam_control_keyboard():
    """Клавиатура управления экзаменом."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏹ Остановить экзамен")]],
        resize_keyboard=True
    )


def create_stop_exam_keyboard():
    """Клавиатура только с кнопкой остановки."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏹ Остановить экзамен")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )