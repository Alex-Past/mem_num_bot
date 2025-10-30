from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from create_bot import bot, notification_manager
from keyboards.notifications_kb import create_notifications_keyboard, create_time_selection_keyboard
from keyboards.mem_kb import main_mem_kb

notifications_router = Router()


class NotificationStates(StatesGroup):
    choosing_time = State()


@notifications_router.message(F.text == '🔔 Уведомления')
async def notifications_settings(message: Message, state: FSMContext):
    """Настройка уведомлений."""
    await state.clear()
    
    user_id = message.from_user.id
    is_active = notification_manager.is_user_active(user_id)
    notification_time = notification_manager.get_user_notification_time(user_id)
    
    await message.answer(
        f"🔔 Настройка уведомлений\n\n"
        f"Статус: {'🔔 Включены' if is_active else '🔕 Выключены'}\n"
        f"Текущее время: {notification_time}\n\n"
        f"Вы можете включить уведомления о сложных карточках и установить удобное время для их получения:",
        reply_markup=create_notifications_keyboard(is_active)
    )


@notifications_router.callback_query(F.data == 'toggle_difficult_notes_notifications')
async def toggle_difficult_notes_notifications(call: CallbackQuery):
    """Включение/выключение уведомлений о сложных карточках."""
    user_id = call.from_user.id
    
    if notification_manager.is_user_active(user_id):
        notification_manager.remove_user(user_id)
        await call.answer("🔕 Уведомления о сложных карточках выключены")
    else:
        notification_manager.add_user(user_id)
        await call.answer("🔔 Уведомления о сложных карточках включены")
    
    # Обновляем клавиатуру
    is_active = notification_manager.is_user_active(user_id)
    notification_time = notification_manager.get_user_notification_time(user_id)
    
    await call.message.edit_text(
        f"🔔 Настройка уведомлений\n\n"
        f"Статус: {'🔔 Включены' if is_active else '🔕 Выключены'}\n"
        f"Текущее время: {notification_time}\n\n"
        f"Вы можете включить уведомления о сложных карточках и установить удобное время для их получения:",
        reply_markup=create_notifications_keyboard(is_active)
    )


@notifications_router.callback_query(F.data == 'set_notification_time')
async def set_notification_time(call: CallbackQuery, state: FSMContext):
    """Установка времени для уведомлений."""
    await call.message.answer(
        "⏰ Выберите время для уведомлений:",
        reply_markup=create_time_selection_keyboard()
    )
    await state.set_state(NotificationStates.choosing_time)


@notifications_router.callback_query(NotificationStates.choosing_time, F.data.startswith('time_'))
async def process_time_selection(call: CallbackQuery, state: FSMContext):
    """Обработка выбора времени."""
    time_str = call.data.replace('time_', '')
    user_id = call.from_user.id
    
    # Сохраняем время для пользователя
    notification_manager.set_user_notification_time(user_id, time_str)
    
    # Включаем уведомления, если они были выключены
    if not notification_manager.is_user_active(user_id):
        notification_manager.add_user(user_id)
    
    await call.message.edit_text(
        f"✅ Время уведомлений установлено на {time_str}\n\n"
        f"Вы будете получать уведомления о сложных карточках ежедневно в это время.",
        reply_markup=create_notifications_keyboard(True)
    )
    await state.clear()


@notifications_router.callback_query(F.data == 'notifications_back')
async def notifications_back(call: CallbackQuery, state: FSMContext):
    """Возврат из настроек уведомлений."""
    await call.message.answer(
        "Главное меню:",
        reply_markup=main_mem_kb()
    )
    await call.message.delete()
    await state.clear()