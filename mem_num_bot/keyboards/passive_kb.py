from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_passive_categories_keyboard(categories, selected_categories=None):
    """Клавиатура для выбора категорий пассивного обучения."""
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
                callback_data=f"passive_category_{category['id']}"
            )
        ])
    
    # Кнопки управления
    keyboard.append([
        InlineKeyboardButton(text="Все категории", callback_data="passive_category_all")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🚀 Продолжить", callback_data="start_passive")
    ])
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Меню", callback_data="passive_back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_interval_keyboard():
    """Клавиатура для выбора интервала."""
    keyboard = [
        [
            InlineKeyboardButton(text="⏱ 15 минут", callback_data="interval_15min")
        ],
        [
            InlineKeyboardButton(text="⏱ 30 минут", callback_data="interval_30min")
        ],
        [
            InlineKeyboardButton(text="⏱ 1 час", callback_data="interval_1hour")
        ],
        [
            InlineKeyboardButton(text="⏱ 2 часа", callback_data="interval_2hours")
        ],
        [
            InlineKeyboardButton(text="⏱ 3 часа", callback_data="interval_3hours")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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