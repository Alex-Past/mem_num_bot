from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import random

from data_base.dao import get_all_categories, get_notes_by_categories
from keyboards.passive_kb import create_passive_categories_keyboard, create_interval_keyboard
from create_bot import bot
from keyboards.note_kb import main_note_kb
from keyboards.mem_kb import main_mem_kb
from utils_bot.utils import send_message_user

passive_router = Router()

# Храним активные пассивные сессии
active_passive_sessions = {}

class PassiveStates(StatesGroup):
    choosing_categories = State()
    choosing_interval = State()
    in_session = State()


@passive_router.message(F.text == "📖 Пассивно")
async def start_passive(message: Message, state: FSMContext):
    """Начало настройки пассивного обучения."""
    await state.clear()
    
    user_id = message.from_user.id
    
    # Проверяем, есть ли активная сессия пассивного обучения
    if user_id in active_passive_sessions and active_passive_sessions[user_id]['active']:
        session = active_passive_sessions[user_id]
        total_notes = len(session['all_notes'])
        shown_notes = len(session['shown_notes'])
        remaining_notes = len(session['available_notes'])
        
        interval_text = {
            1800: "30 минут",
            3600: "1 час", 
            7200: "2 часа",
            10800: "3 часа"
        }.get(session['interval'], f"{session['interval']//3600} часа")
        
        await message.answer(
            f"📖 Пассивное обучение уже запущено!\n\n"
            f"• Всего карточек: {total_notes}\n"
            f"• Показано: {shown_notes}\n"
            f"• Осталось: {remaining_notes}\n"
            f"• Интервал: {interval_text}\n\n"
            f"Вы можете остановить обучение или продолжить.",
            reply_markup=create_stop_passive_keyboard()
        )
        await state.set_state(PassiveStates.in_session)
        return
    
    # Если активной сессии нет, показываем обычное меню
    categories = await get_all_categories(user_id=user_id)
    if not categories:
        await message.answer(
            "❌ У вас нет категорий для пассивного обучения.",
            reply_markup=main_note_kb()  # Исправлено: было reply_mup
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
        await state.update_data(selected_categories=category_ids)
        await show_interval_selection(call, state)
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
    
    await show_interval_selection(call, state)


async def show_interval_selection(call: CallbackQuery, state: FSMContext):
    """Показ выбора интервала."""
    await call.message.answer(
        "⏰ Выберите интервал отправки карточек:",
        reply_markup=create_interval_keyboard()
    )
    await state.set_state(PassiveStates.choosing_interval)


@passive_router.callback_query(PassiveStates.choosing_interval, F.data.startswith('interval_'))
async def process_interval_selection(call: CallbackQuery, state: FSMContext):
    """Обработка выбора интервала."""
    interval_map = {
        'interval_30min': 1800,  # 30 минут
        'interval_1hour': 3600,  # 1 час
        'interval_2hours': 7200,  # 2 часа
        'interval_3hours': 10800  # 3 часа
    }
    
    interval_key = call.data
    interval_seconds = interval_map.get(interval_key)
    
    if not interval_seconds:
        await call.answer("❌ Неверный интервал", show_alert=True)
        return
    
    # Получаем выбранные категории
    data = await state.get_data()
    selected_categories = data.get('selected_categories', [])
    
    await start_passive_session(call, state, selected_categories, interval_seconds)


async def start_passive_session(call: CallbackQuery, state: FSMContext, category_ids: list, interval_seconds: int):
    """Запуск пассивной сессии."""
    user_id = call.from_user.id
    
    # Останавливаем предыдущую сессию, если есть
    if user_id in active_passive_sessions:
        active_passive_sessions[user_id]['active'] = False
        # Даем время на завершение предыдущей задачи
        await asyncio.sleep(1)
    
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
    
    # Перемешиваем карточки для равномерного распределения
    shuffled_notes = notes.copy()
    random.shuffle(shuffled_notes)
    
    # Создаем сессию с улучшенной логикой
    active_passive_sessions[user_id] = {
        'active': True,
        'all_notes': notes,  # Все карточки
        'available_notes': shuffled_notes,  # Доступные для показа
        'shown_notes': [],  # Показанные карточки
        'interval': interval_seconds,
        'last_message_id': None,
        'current_note': None,
        'last_sent_time': None  # Время последней отправки
    }
    
    # Показываем информацию о запуске
    interval_text = {
        1800: "30 минут",
        3600: "1 час", 
        7200: "2 часа",
        10800: "3 часа"
    }.get(interval_seconds, f"{interval_seconds//3600} часа")
    
    await call.message.answer(
        f"📖 Пассивное обучение запущено!\n"
        f"• Категории: {len(category_ids)}\n"
        f"• Карточек: {len(notes)}\n"
        f"• Интервал: {interval_text}\n\n"
        f"Я буду присылать случайные карточки с выбранным интервалом.\n"
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
    builder.button(text="📋 Главное меню")
    builder.adjust(2)  # 2 кнопки в одной строке
    return builder.as_markup(resize_keyboard=True)


async def passive_worker(user_id: int):
    """Фоновая задача для отправки карточек по расписанию."""
    while user_id in active_passive_sessions and active_passive_sessions[user_id]['active']:
        try:
            session = active_passive_sessions[user_id]
            interval = session.get('interval', 3600)
            
            # Ждем выбранный интервал
            await asyncio.sleep(interval)
            
            # Проверяем, активна ли еще сессия и нет ли активной карточки
            if (user_id in active_passive_sessions and 
                active_passive_sessions[user_id]['active'] and
                not session.get('current_note')):
                
                await send_random_passive_card(user_id)
                    
        except Exception as e:
            print(f"Ошибка в passive_worker: {e}")
            break


async def send_random_passive_card(user_id: int):
    """Отправляет случайную карточку пользователю с улучшенной логикой."""
    if user_id not in active_passive_sessions:
        return
    
    session = active_passive_sessions[user_id]
    if not session['active']:
        return
    
    # Если доступные карточки закончились, перемешиваем заново
    if not session['available_notes']:
        # Перемешиваем все карточки заново
        all_notes = session['all_notes'].copy()
        random.shuffle(all_notes)
        
        session['available_notes'] = all_notes
        session['shown_notes'] = []
    
    # Берем следующую карточку из доступных
    random_note = session['available_notes'].pop(0)
    session['shown_notes'].append(random_note)
    
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


@passive_router.message(PassiveStates.in_session, F.text == "📋 Главное меню")
async def go_to_main_menu(message: Message, state: FSMContext):
    """Переход в главное меню без остановки пассивного обучения."""
    await message.answer(
        "Вы в главном меню. Пассивное обучение продолжается в фоне.",
        reply_markup=main_mem_kb()
    )
    # Состояние не очищаем, чтобы пассивное обучение продолжалось


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
    
    # Задержка перед показом полной карточки
    await asyncio.sleep(0.8)
    
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
    
    # Очищаем текущую карточку из сессии
    session['current_note'] = None