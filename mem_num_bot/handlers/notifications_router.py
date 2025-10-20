from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from create_bot import bot, notification_manager
from keyboards.notifications_kb import create_notifications_keyboard
from keyboards.note_kb import main_note_kb

notifications_router = Router()

@notifications_router.message(F.text == '🔔 Уведомления')
async def notifications_settings(message: Message, state: FSMContext):
    """Настройка уведомлений."""
    await state.clear()
    
    is_active = notification_manager.is_user_active(message.from_user.id)
    
    await message.answer(
        "🔔 Настройка уведомлений\n\n"
        "Вы можете включить или выключить следующие уведомления:",
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
    await call.message.edit_reply_markup(
        reply_markup=create_notifications_keyboard(is_active)
    )


@notifications_router.callback_query(F.data == 'notifications_back')
async def notifications_back(call: CallbackQuery, state: FSMContext):
    """Возврат из настроек уведомлений."""
    await call.message.answer(
        "Главное меню:",
        reply_markup=main_note_kb()
    )
    await call.message.delete()