from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
from datetime import datetime, timedelta

from data_base.dao import get_all_categories, get_notes_by_categories
from keyboards.passive_kb import create_passive_categories_keyboard
from create_bot import bot
from keyboards.note_kb import main_note_kb
from keyboards.mem_kb import main_mem_kb
from utils_bot.utils import send_message_user

passive_router = Router()

# Храним активные пассивные сессии
active_passive_sessions = {}

class PassiveStates(StatesGroup):
    choosing_categories = State()
    in_session = State()


@passive_router.message(F.text == "📖 Пассивно")
async def start_passive(message: Message, state: FSMContext):
    """Начало настройки пассивного обучения."""
    await state.clear()
    
    categories = await get_all_categories(user_id=message.from_user.id)
    if not categories:
        await message.answer(
            "❌ У вас нет категорий для пассивного обучения.",
            reply_markup=main_note_kb()
        )
        return
    
    await message.answer(
        "📖 Выберите категории для пассивного обучения:\n\n"
        "• Можно выбрать несколько категорий\n"
        "• Или нажмите 'Все категории' для обучения по всем заметкам",
        reply_markup=create_passive_categories_keyboard(categories)
    )
    await state.set_state(PassiveStates.choosing_categories)


@passive_router.callback_query(PassiveStates.choosing_categories, F.data.startswith('passive_category_'))
async def process_passive_category_selection(call: CallbackQuery, state: FSMContext):
    """Обработка выбора категорий для пассивного обучения."""
    data = await state.get_data()
    selected_categories = data.get('selected_categories', [])
    
    if call.data == 'passive_category_all':
        # Выбраны все категории
        categories = await get_all_categories(user_id=call.from_user.id)
        category_ids = [cat['id'] for cat in categories]
        await start_passive_session(call, state, category_ids)
        return
    
    category_id = int(call.data.replace('passive_category_', ''))
    
    if category_id in selected_categories:
        selected_categories.remove(category_id)
    else:
        selected_categories.append(category_id)
    
    await state.update_data(selected_categories=selected_categories)
    
    # Обновляем клавиатуру с выделенными категориями
    categories = await get_all_categories(user_id=call.from_user.id)
    await call.message.edit_reply_markup(
        reply_markup=create_passive_categories_keyboard(categories, selected_categories)
    )
    await call.answer()


@passive_router.callback_query(PassiveStates.choosing_categories, F.data == 'start_passive')
async def start_passive_with_selected(call: CallbackQuery, state: FSMContext):
    """Начало пассивного обучения с выбранными категориями."""
    data = await state.get_data()
    selected_categories = data.get('selected_categories', [])
    
    if not selected_categories:
        await call.answer("❌ Выберите хотя бы одну категорию!", show_alert=True)
        return
    
    await start_passive_session(call, state, selected_categories)


async def start_passive_session(call: CallbackQuery, state: FSMContext, category_ids: list):
    """Запуск пассивной сессии."""
    user_id = call.from_user.id
    
    # Останавливаем предыдущую сессию, если есть
    if user_id in active_passive_sessions:
        active_passive_sessions[user_id]['active'] = False
    
    # Получаем заметки для пассивного обучения
    notes = await get_notes_by_categories(
        user_id=user_id,
        category_ids=category_ids
    )
    
    if not notes:
        await call.message.answer(
            "❌ В выбранных категориях нет карточек!",
            reply_markup=main_note_kb()
        )
        await state.clear()
        return
    
    # Создаем сессию
    active_passive_sessions[user_id] = {
        'active': True,
        'notes': notes,
        'category_ids': category_ids,
        'last_message_id': None
    }
    
    await call.message.answer(
        f"📖 Пассивное обучение запущено!\n"
        f"Категории: {len(category_ids)}\n"
        f"Карточек: {len(notes)}\n\n"
        f"Я буду присылать случайные карточки каждый час с 8:00 до 23:00.\n"
        f"Вы можете остановить в любой момент.",
        reply_markup=create_stop_passive_keyboard()
    )
    
    # Запускаем первую карточку сразу
    await send_random_passive_card(user_id)
    
    # Запускаем периодическую отправку
    asyncio.create_task(passive_worker(user_id))
    
    await state.set_state(PassiveStates.in_session)


def create_stop_passive_keyboard():
    """Клавиатура для остановки пассивного обучения."""
    builder = ReplyKeyboardBuilder()
    builder.button(text="⏹ Остановить пассивное обучение")
    return builder.as_markup(resize_keyboard=True)


async def passive_worker(user_id: int):
    """Фоновая задача для отправки карточек по расписанию."""
    while user_id in active_passive_sessions and active_passive_sessions[user_id]['active']:
        try:
            # Ждем 1 час
            await asyncio.sleep(3600)
            
            # Проверяем время (8:00 - 23:00)
            current_hour = datetime.now().hour
            if 8 <= current_hour <= 23:
                if user_id in active_passive_sessions and active_passive_sessions[user_id]['active']:
                    await send_random_passive_card(user_id)
                    
        except Exception as e:
            print(f"Ошибка в passive_worker: {e}")
            break


async def send_random_passive_card(user_id: int):
    """Отправляет случайную карточку пользователю."""
    if user_id not in active_passive_sessions:
        return
    
    session = active_passive_sessions[user_id]
    if not session['active']:
        return
    
    import random
    notes = session['notes']
    
    if not notes:
        return
    
    # Выбираем случайную карточку
    random_note = random.choice(notes)
    
    # Удаляем предыдущее сообщение, если есть
    if session.get('last_message_id'):
        try:
            await bot.delete_message(user_id, session['last_message_id'])
        except:
            pass
    
    # Отправляем название карточки
    message = await bot.send_message(
        user_id,
        f"📖 Пассивное обучение\n\n"
        # f"Категория: {random_note.get('category_name', 'Без категории')}\n"
        f"{random_note.get('content_text', 'Без названия')}\n\n"
        f"Напиши описание этой карточки:",
        reply_markup=create_stop_passive_keyboard()
    )
    
    # Сохраняем данные карточки для проверки ответа
    session['current_note'] = random_note
    session['last_message_id'] = message.message_id


@passive_router.message(PassiveStates.in_session, F.text == "⏹ Остановить пассивное обучение")
async def stop_passive_learning(message: Message, state: FSMContext):
    """Остановка пассивного обучения."""
    user_id = message.from_user.id
    
    if user_id in active_passive_sessions:
        active_passive_sessions[user_id]['active'] = False
        del active_passive_sessions[user_id]
    
    await message.answer(
        "⏹ Пассивное обучение остановлено!",
        reply_markup=main_mem_kb()
    )
    await state.clear()


@passive_router.message(PassiveStates.in_session)
async def check_passive_answer(message: Message, state: FSMContext):
    """Проверка ответа в пассивном режиме."""
    user_id = message.from_user.id
    
    if user_id not in active_passive_sessions:
        return
    
    session = active_passive_sessions[user_id]
    if not session.get('current_note'):
        return
    
    current_note = session['current_note']
    user_answer = message.text.strip().lower()
    correct_description = (current_note.get('description') or '').strip().lower()
    
    # Проверяем ответ
    is_correct = user_answer == correct_description
    
    # Отправляем результат
    if is_correct:
        await message.answer("✅ Верно!")
    else:
        await message.answer("❌ Не верно!")
    
    await asyncio.sleep(0,8)
    
    # Показываем полную карточку в любом случае
    full_card_text = (
        f"📖 Полная карточка:\n\n"
        f"Категория: {current_note.get('category_name', 'Без категории')}\n"
        f"Название: {current_note.get('content_text', 'Без названия')}\n"
        f"Описание: {current_note.get('description', 'Отсутствует')}"
    )
    
    await send_message_user(
        bot=bot,
        content_type=current_note.get('content_type'),
        content_text=full_card_text,
        user_id=user_id,
        file_id=current_note.get('file_id'),
        kb=create_stop_passive_keyboard()
    )
    
    # Удаляем текущую карточку из сессии
    session['current_note'] = None