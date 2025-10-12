from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from data_base.dao import get_notes_count, get_random_note
from keyboards.note_kb import main_note_kb
from keyboards.mem_kb import create_random_card_keyboard, main_mem_kb
from create_bot import bot
from utils_bot.utils import send_message_user

random_card_router = Router()


@random_card_router.message(F.text == '🎲 Случайная карточка')
async def show_random_card(message: Message, state: FSMContext):
    await state.clear()
    
    # Проверяем, есть ли заметки
    notes_count = await get_notes_count(user_id=message.from_user.id)
    
    if notes_count == 0:
        await message.answer(
            "📝 У вас пока нет заметок. Создайте первую заметку!",
            reply_markup=main_note_kb()
        )
        return
    
    # Получаем случайную заметку
    random_note = await get_random_note(user_id=message.from_user.id)
    
    if not random_note:
        await message.answer(
            "❌ Не удалось получить случайную заметку",
            reply_markup=main_note_kb()
        )
        return
    
    # Сохраняем данные заметки для показа по кнопке
    await state.update_data(random_note=random_note)
    
    # Формируем заголовок (используем первые 100 символов текста или описание)
    preview_text = random_note.get('content_text') or "Заметка без текста"
    if len(preview_text) > 100:
        preview_text = preview_text[:100] + "..."
    
    # Отправляем превью с кнопкой
    await message.answer(
        f"🎲 Случайная карточка\n\n"
        # f"Категория: {random_note['category_name']}\n"
        f"Текст: {preview_text}",
        reply_markup=create_random_card_keyboard()
    )


@random_card_router.callback_query(F.data == 'show_full_random_note')
async def show_full_random_note(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    random_note = data.get('random_note')
    
    if not random_note:
        await call.answer("❌ Данные заметки не найдены", show_alert=True)
        return
    
    # Формируем полный текст заметки
    text = (f"🎲 Случайная карточка\n\n"
            f"Категория: {random_note['category_name']}\n"
            f"Текст:\n{random_note['content_text'] or 'Отсутствует'}\n\n"
            f"Описание:\n{random_note['description'] or 'Отсутствует'}")
    
    # Отправляем полную версию
    await send_message_user(
        bot=bot,
        content_type=random_note['content_type'],
        content_text=text,
        user_id=call.from_user.id,
        file_id=random_note['file_id'],
        kb=main_mem_kb()
    )
    
    await call.message.delete()
    await state.clear()


# @random_card_router.callback_query(F.data == 'another_random_card')
# async def show_another_random_card(call: CallbackQuery, state: FSMContext):
#     await call.message.delete()
#     await show_random_card(call.message, state)