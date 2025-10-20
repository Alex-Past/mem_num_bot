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
        InlineKeyboardButton(text="🎯 Все категории", callback_data="passive_category_all")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🚀 Начать обучение", callback_data="start_passive")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)