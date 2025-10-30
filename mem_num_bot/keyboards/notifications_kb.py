from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_notifications_keyboard(is_active: bool):
    """Клавиатура для настроек уведомлений."""
    status_icon = "🔔" if is_active else "🔕"
    status_text = "Выключить" if is_active else "Включить"
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{status_icon} {status_text} уведомления",
                callback_data="toggle_difficult_notes_notifications"
            )
        ],
        [
            InlineKeyboardButton(
                text="⏰ Установить время",
                callback_data="set_notification_time"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад", 
                callback_data="notifications_back"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_time_selection_keyboard():
    """Клавиатура для выбора времени уведомлений."""
    # Создаем кнопки для популярных времен
    times = [
        "08:00", "09:00", "10:00", "11:00", "12:00",
        "13:00", "14:00", "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00", "21:00", "22:00"
    ]
    
    keyboard = []
    row = []
    
    for i, time_str in enumerate(times):
        row.append(InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}"))
        if len(row) == 3 or i == len(times) - 1:
            keyboard.append(row)
            row = []
    
    # Добавляем кнопку назад
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="notifications_back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)