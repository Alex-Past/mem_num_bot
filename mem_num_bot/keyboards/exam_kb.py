from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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
        InlineKeyboardButton(text="Все категории", callback_data="exam_category_all")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🚀 Начать экзамен", callback_data="start_exam")
    ])
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Меню", callback_data="exam_back")
    ])
    
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


def create_show_file_keyboard():
    """Клавиатура для выбора показа файла."""
    keyboard = [
        [
            InlineKeyboardButton(text="📝 Только текст", callback_data="show_file_false")
        ],
        [
            InlineKeyboardButton(text="🎆 Текст + файл", callback_data="show_file_true")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)