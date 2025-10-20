from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_notifications_keyboard(is_active: bool):
    """Клавиатура для настроек уведомлений."""
    status_icon = "🔔" if is_active else "🔕"
    status_text = "Выключить" if is_active else "Включить"
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{status_icon} {status_text} уведомления о сложных карточках",
                callback_data="toggle_difficult_notes_notifications"
            )
        ],
        # [
        #     InlineKeyboardButton(
        #         text="📊 Статистика уведомлений", 
        #         callback_data="notifications_stats"
        #     )
        # ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад", 
                callback_data="notifications_back"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)