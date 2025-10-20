import asyncio
import random

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from data_base.dao import (
    get_all_categories,
    get_difficult_notes,
    get_note_by_id, 
    get_notes_by_categories, 
    update_note_stats
)
from keyboards.exam_kb import (
    create_categories_keyboard, 
    create_exam_control_keyboard,
    create_exam_main_keyboard,
    create_stop_exam_keyboard
)
from create_bot import bot
from keyboards.note_kb import main_note_kb
from keyboards.mem_kb import main_mem_kb
from utils_bot.utils import send_message_user

exam_router = Router()


class ExamStates(StatesGroup):
    choosing_categories = State()
    in_exam = State()


@exam_router.message(F.text == '📚 Экзамен')
async def start_exam(message: Message, state: FSMContext):
    """Начало экзамена - выбор режима."""
    await state.clear()
    
    # Проверяем, есть ли сложные карточки
    difficult_notes = await get_difficult_notes(user_id=message.from_user.id)
    has_difficult = len(difficult_notes) > 0
    
    text = "📚 Выберите режим экзамена:"
    if has_difficult:
        text += f"\n\n🎯 У вас {len(difficult_notes)} сложных карточек для повторения"
    
    await message.answer(
        text,
        reply_markup=create_exam_main_keyboard(has_difficult_notes=has_difficult)
    )

@exam_router.callback_query(F.data == 'difficult_notes')
async def start_difficult_exam(call: CallbackQuery, state: FSMContext):
    """Начало экзамена по сложным карточкам."""
    difficult_notes = await get_difficult_notes(user_id=call.from_user.id)
    
    if not difficult_notes:
        await call.answer("❌ У вас пока нет сложных карточек!", show_alert=True)
        return
    
    # Перемешиваем сложные карточки
    import random
    random.shuffle(difficult_notes)
    
    await state.update_data(
        exam_notes=difficult_notes,
        current_note_index=0,
        correct_answers=0,
        wrong_answers=0,
        wrong_notes=[],
        exam_mode="difficult"  # Добавляем метку режима
    )
    
    await call.message.answer(
        f"🎯 Начинаем повторение сложных карточек!\n"
        f"Всего карточек: {len(difficult_notes)}\n\n"
        f"Старайтесь запомнить эти карточки - они требуют больше внимания!",
        reply_markup=create_stop_exam_keyboard()
    )
    
    await show_next_exam_question(call.message, state)
    await state.set_state(ExamStates.in_exam)


@exam_router.callback_query(F.data == 'select_categories')
async def select_categories_mode(call: CallbackQuery, state: FSMContext):
    """Вход в режим выбора категорий из главного меню."""
    categories = await get_all_categories(user_id=call.from_user.id)
    if not categories:
        await call.message.answer(
            "❌ У вас нет категорий для экзамена.",
            reply_markup=main_note_kb()
        )
        return
    
    await call.message.answer(
        "📚 Выберите категории для экзамена:",
        reply_markup=create_categories_keyboard(categories)
    )
    await state.set_state(ExamStates.choosing_categories)


@exam_router.callback_query(ExamStates.choosing_categories, F.data.startswith('exam_category_'))
async def process_category_selection(call: CallbackQuery, state: FSMContext):
    """Обработка выбора категорий."""
    data = await state.get_data()
    selected_categories = data.get('selected_categories', [])
    
    if call.data == 'exam_category_all':
        # Выбраны все категории
        categories = await get_all_categories(user_id=call.from_user.id)
        category_ids = [cat['id'] for cat in categories]
        await state.update_data(selected_categories=category_ids)
        await start_exam_session(call, state, category_ids)
        return
    
    category_id = int(call.data.replace('exam_category_', ''))
    
    if category_id in selected_categories:
        selected_categories.remove(category_id)
    else:
        selected_categories.append(category_id)
    
    await state.update_data(selected_categories=selected_categories)
    
    # Обновляем клавиатуру с выделенными категориями
    categories = await get_all_categories(user_id=call.from_user.id)
    await call.message.edit_reply_markup(
        reply_markup=create_categories_keyboard(categories, selected_categories)
    )
    await call.answer()


@exam_router.callback_query(ExamStates.choosing_categories, F.data == 'start_exam')
async def start_exam_with_selected(call: CallbackQuery, state: FSMContext):
    """Начало экзамена с выбранными категориями."""
    data = await state.get_data()
    selected_categories = data.get('selected_categories', [])
    
    if not selected_categories:
        await call.answer("❌ Выберите хотя бы одну категорию!", show_alert=True)
        return
    
    await start_exam_session(call, state, selected_categories)


async def start_exam_session(call: CallbackQuery, state: FSMContext, category_ids: list):
    """Запуск сессии экзамена."""
    # Получаем заметки для экзамена
    notes = await get_notes_by_categories(
        user_id=call.from_user.id,
        category_ids=category_ids
    )
    
    # Фильтруем заметки с описанием
    exam_notes = [note for note in notes if note.get('description')]
    
    if not exam_notes:
        await call.message.answer(
            "❌ В выбранных категориях нет карточек с описанием для экзамена!",
            reply_markup=main_note_kb()
        )
        await state.clear()
        return
    
    # Перемешиваем заметки
    random.shuffle(exam_notes)
    
    await state.update_data(
        exam_notes=exam_notes,
        current_note_index=0,
        correct_answers=0,
        wrong_answers=0,
        wrong_notes=[]
    )
    
    await call.message.answer(
        f"📚 Экзамен начался!\n"
        f"Всего карточек: {len(exam_notes)}\n\n"
        f"Я буду показывать название карточки, а ты напиши описание к ней.\n"
        f"В любой момент можно остановить экзамен.",
        reply_markup=create_stop_exam_keyboard()
    )
    
    await show_next_exam_question(call.message, state)
    await state.set_state(ExamStates.in_exam)


async def show_next_exam_question(message: Message, state: FSMContext):
    """Показ следующего вопроса экзамена."""
    data = await state.get_data()
    exam_notes = data.get('exam_notes', [])
    current_index = data.get('current_note_index', 0)
    
    if current_index >= len(exam_notes):
        # Экзамен завершен
        await finish_exam(message, state)
        return
    
    current_note = exam_notes[current_index]

    await asyncio.sleep(0,8)
    await message.answer(
        f"Карточка {current_index + 1}/{len(exam_notes)}\n\n"
        f"{current_note.get('content_text', 'Без названия')}\n\n"
        f"Напиши описание этой карточки:",
        reply_markup=create_stop_exam_keyboard()
    )


@exam_router.message(ExamStates.in_exam, F.text == "⏹ Остановить экзамен")
async def stop_exam(message: Message, state: FSMContext):
    """Остановка экзамена по требованию пользователя."""
    data = await state.get_data()
    current_index = data.get('current_note_index', 0)
    total_notes = len(data.get('exam_notes', []))
    
    await message.answer(
        f"⏹ Экзамен остановлен!\n"
        f"Пройдено карточек: {current_index}/{total_notes}",
        reply_markup=main_mem_kb()
    )
    await state.clear()


@exam_router.message(ExamStates.in_exam)
async def check_exam_answer(message: Message, state: FSMContext):
    """Проверка ответа пользователя."""
    data = await state.get_data()
    exam_notes = data.get('exam_notes', [])
    current_index = data.get('current_note_index', 0)
    correct_answers = data.get('correct_answers', 0)
    wrong_answers = data.get('wrong_answers', 0)
    wrong_notes = data.get('wrong_notes', [])
    
    if current_index >= len(exam_notes):
        return
    
    current_note = exam_notes[current_index]
    user_answer = message.text.strip().lower()
    correct_description = (current_note.get('description') or '').strip().lower()
    
    # Проверяем ответ
    is_correct = user_answer == correct_description
    
    # Обновляем статистику
    if is_correct:
        correct_answers += 1
        await update_note_stats(current_note['id'], correct=True)
        await message.answer("✅ Верно!")
    else:
        wrong_answers += 1
        wrong_notes.append(current_note)
        await update_note_stats(current_note['id'], correct=False)
        await message.answer("❌ Не верно!")

    await asyncio.sleep(0,8)

    # Переходим к следующему вопросу (НЕ показываем полную карточку)
    current_index += 1
    await state.update_data(
        current_note_index=current_index,
        correct_answers=correct_answers,
        wrong_answers=wrong_answers,
        wrong_notes=wrong_notes
    )
    
    await show_next_exam_question(message, state)


async def finish_exam(message: Message, state: FSMContext):
    """Завершение экзамена и показ результатов."""
    data = await state.get_data()
    correct_answers = data.get('correct_answers', 0)
    wrong_answers = data.get('wrong_answers', 0)
    wrong_notes = data.get('wrong_notes', [])
    total_notes = len(data.get('exam_notes', []))
    
    # Статистика
    success_rate = (correct_answers / total_notes * 100) if total_notes > 0 else 0
    
    result_text = (
        f"🎉 Экзамен завершен!\n\n"
        f"📊 Результаты:\n"
        f"✅ Правильных ответов: {correct_answers}\n"
        f"❌ Неправильных ответов: {wrong_answers}\n"
        f"📈 Успешность: {success_rate:.1f}%"
    )
    
    await message.answer(result_text, reply_markup=main_mem_kb())

    await asyncio.sleep(0,8)
    
    # Показываем список не угаданных карточек с кнопками "показать"
    if wrong_notes:
        await message.answer("📝 Карточки, в которых вы ошиблись:")
        
        for note in wrong_notes:
            # Обрезаем длинное название для красоты
            note_title = note.get('content_text', 'Без названия')
            if len(note_title) > 50:
                note_title = note_title[:50] + "..."
                
            # Создаем кнопку для каждой карточки
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            show_button = InlineKeyboardButton(
                text="🃏 Показать карточку", 
                callback_data=f"show_wrong_note_{note['id']}"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[show_button]])
            
            await message.answer(
                f"❌ {note_title}",
                reply_markup=keyboard
            )
    
    await state.clear()


@exam_router.callback_query(F.data.startswith('show_wrong_note_'))
async def show_wrong_note(call: CallbackQuery):
    """Показ полной карточки из списка ошибок."""
    note_id = int(call.data.replace('show_wrong_note_', ''))
    
    # Получаем карточку из базы
    note = await get_note_by_id(note_id)
    
    if not note:
        await call.answer("❌ Карточка не найдена", show_alert=True)
        return
    
    # Формируем полный текст карточки
    full_card_text = (
        f"📚 Карточка из ошибок:\n\n"
        f"Категория: {note.get('category_name', 'Без категории')}\n"
        f"Название: {note.get('content_text', 'Без названия')}\n"
        f"Описание: {note.get('description', 'Отсутствует')}"
    )
    
    # Отправляем полную карточку
    await send_message_user(
        bot=bot,
        content_type=note.get('content_type'),
        content_text=full_card_text,
        user_id=call.from_user.id,
        file_id=note.get('file_id')
    )
    
    await call.answer()    