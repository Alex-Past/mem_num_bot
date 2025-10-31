from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import random

from data_base.dao import (
    get_all_categories, 
    get_notes_by_categories, 
    update_note_stats,
    get_difficult_notes
)
from keyboards.exam_kb import (
    create_categories_keyboard,    
    create_stop_exam_keyboard,
    create_show_file_keyboard
)
from create_bot import bot
from keyboards.mem_kb import main_mem_kb
from utils_bot.utils import send_message_user
from keyboards.note_kb import main_note_kb

exam_router = Router()


class ExamStates(StatesGroup):
    choosing_categories = State()
    choosing_show_file = State()
    in_exam = State()
    finished = State()


@exam_router.message(F.text == '🧠 Экзамен')
async def start_exam(message: Message, state: FSMContext):
    """Начало экзамена - выбор режима."""
    await state.clear()
    
    # Проверяем, есть ли сложные карточки
    difficult_notes = await get_difficult_notes(user_id=message.from_user.id)
    has_difficult = len(difficult_notes) > 0
    
    text = "🧠 Выберите режим экзамена:"
    if has_difficult:
        text += f"\n\n🎯 Cложных карточек для повторения: {len(difficult_notes)}"
    
    keyboard = [
        [InlineKeyboardButton(text="📚 Выбрать категории", callback_data="select_categories")],
    ]
    
    if has_difficult:
        keyboard.append([
            InlineKeyboardButton(text="🎯 Повторить сложные", callback_data="difficult_notes")
        ])

    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@exam_router.callback_query(F.data == 'select_categories')
async def select_categories_mode(call: CallbackQuery, state: FSMContext):
    """Режим выбора категорий."""
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
    """Обработка выбора категорий в меню выбора."""
    data = await state.get_data()
    selected_categories = data.get('selected_categories', [])
    
    if call.data == 'exam_category_all':
        # Выбраны все категории
        categories = await get_all_categories(user_id=call.from_user.id)
        category_ids = [cat['id'] for cat in categories]
        await state.update_data(selected_categories=category_ids)
        await show_show_file_selection(call, state)
        return
    
    if call.data == 'exam_back':
        await exam_back(call, state)
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
    
    await show_show_file_selection(call, state)


@exam_router.callback_query(ExamStates.choosing_categories, F.data == 'exam_back')
async def exam_back(call: CallbackQuery, state: FSMContext):
    """Возврат из выбора категорий экзамена."""
    await call.message.answer(
        "🧩 Главное меню:",
        reply_markup=main_mem_kb()
    )
    await call.message.delete()
    await state.clear()


async def show_show_file_selection(call: CallbackQuery, state: FSMContext):
    """Показ выбора показа файла."""
    await call.message.answer(
        "📸 Выберите, как показывать карточки:",
        reply_markup=create_show_file_keyboard()
    )
    await state.set_state(ExamStates.choosing_show_file)


@exam_router.callback_query(ExamStates.choosing_show_file, F.data.startswith('show_file_'))
async def process_show_file_selection(call: CallbackQuery, state: FSMContext):
    """Обработка выбора показа файла для всех режимов."""
    show_file = call.data == 'show_file_true'
    
    data = await state.get_data()
    
    # Проверяем режим экзамена
    exam_mode = data.get('exam_mode', 'normal')
    
    if exam_mode == 'difficult':
        # Режим сложных карточек
        difficult_notes = data.get('difficult_notes')
        if difficult_notes:
            await start_difficult_exam_session(call, state, difficult_notes, show_file)
        else:
            await call.answer("❌ Ошибка: сложные карточки не найдены", show_alert=True)
    else:
        # Обычный режим
        selected_categories = data.get('selected_categories', [])
        await start_exam_session(call, state, selected_categories, show_file)


@exam_router.callback_query(F.data == 'difficult_notes')
async def start_difficult_exam(call: CallbackQuery, state: FSMContext):
    """Начало экзамена по сложным карточкам."""
    difficult_notes = await get_difficult_notes(user_id=call.from_user.id)
    
    if not difficult_notes:
        await call.answer("❌ У вас пока нет сложных карточек!", show_alert=True)
        return
        
    await state.update_data(
        difficult_notes=difficult_notes,
        exam_mode="difficult"
    )
    await state.set_state(ExamStates.choosing_show_file)
    
    await call.message.answer(
        "📸 Выберите, как показывать карточки:",
        reply_markup=create_show_file_keyboard()
    )


async def start_exam_session(call: CallbackQuery,
                            state: FSMContext,
                            category_ids: list, show_file: bool):
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
            "❌ В выбранных категориях нет заметок с описанием для экзамена!",
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
        wrong_notes=[],
        exam_mode="normal",
        show_file=show_file,
        selected_categories=category_ids
    )
    
    await call.message.answer(
        f"🧠 Экзамен начался!\n"
        f"Всего карточек: {len(exam_notes)}\n"
        f"Показ файла: {'Да' if show_file else 'Нет'}\n\n"
        f"Я буду показывать карточки, а ты напиши описание к ним.\n"
        f"В любой момент можно остановить экзамен.",
        reply_markup=create_stop_exam_keyboard()
    )
    
    await show_next_exam_question(call.from_user.id, state)
    await state.set_state(ExamStates.in_exam)


async def start_difficult_exam_session(call: CallbackQuery,
                                       state: FSMContext,
                                       difficult_notes: list,
                                       show_file: bool):
    """Запуск экзамена по сложным карточкам."""
    # Перемешиваем сложные карточки
    random.shuffle(difficult_notes)
    
    await state.update_data(
        exam_notes=difficult_notes,
        current_note_index=0,
        correct_answers=0,
        wrong_answers=0,
        wrong_notes=[],
        exam_mode="difficult",
        show_file=show_file
    )
    
    await call.message.answer(
        f"🎯 Начинаем повторение сложных карточек!\n"
        f"Всего карточек: {len(difficult_notes)}\n"
        f"Показ файла: {'Да' if show_file else 'Нет'}\n\n"
        f"Старайтесь запомнить эти карточки - они требуют больше внимания!",
        reply_markup=create_stop_exam_keyboard()
    )
    
    await show_next_exam_question(call.from_user.id, state)
    await state.set_state(ExamStates.in_exam)


async def show_next_exam_question(user_id: int, state: FSMContext):
    """Показ следующего вопроса экзамена."""
    data = await state.get_data()
    exam_notes = data.get('exam_notes', [])
    current_index = data.get('current_note_index', 0)
    show_file = data.get('show_file', False)
    
    if current_index >= len(exam_notes):
        await finish_exam(user_id, state)
        return
    
    current_note = exam_notes[current_index]
    
    # Формируем текст для карточки
    card_text = (f"📝 Карточка {current_index + 1}/{len(exam_notes)}\n\n"
                 f"{current_note.get('content_text', 'Без названия')}"
                 "\n\nНапиши описание этой карточки:")
    
   
    if show_file and current_note.get('file_id') and current_note.get('content_type') != "text":
        try:
            # Показываем карточку с файлом
            await send_message_user(
                bot=bot,
                content_type=current_note.get('content_type'),
                content_text=card_text,
                user_id=user_id,
                file_id=current_note.get('file_id'),
                kb=create_stop_exam_keyboard()
            )
        except Exception as e:
            print(f"❌ Ошибка при отправке файла: {e}")
            # Если ошибка, показываем только текст
            await bot.send_message(
                chat_id=user_id,
                text=card_text,
                reply_markup=create_stop_exam_keyboard()
            )
    else:
        # Показываем только текст
        await bot.send_message(
            chat_id=user_id,
            text=card_text,
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
    
    # Добавляем задержку 1.5 секунды перед следующим вопросом
    await asyncio.sleep(1.5)
    
    # Переходим к следующему вопросу (НЕ показываем полную карточку)
    current_index += 1
    await state.update_data(
        current_note_index=current_index,
        correct_answers=correct_answers,
        wrong_answers=wrong_answers,
        wrong_notes=wrong_notes
    )
    
    await show_next_exam_question(message.from_user.id, state)


async def finish_exam(user_id: int, state: FSMContext):
    """Завершение экзамена и показ результатов."""
    data = await state.get_data()
    correct_answers = data.get('correct_answers', 0)
    wrong_answers = data.get('wrong_answers', 0)
    wrong_notes = data.get('wrong_notes', [])
    total_notes = len(data.get('exam_notes', []))
    selected_categories = data.get('selected_categories', [])
    show_file = data.get('show_file', False)
    exam_mode = data.get('exam_mode', 'normal')
    

    if exam_mode == 'difficult':
        original_difficult_notes = data.get('exam_notes', [])  # Сохраняем исходный список
        await state.update_data(
            repeat_difficult_notes=original_difficult_notes,  # Сохраняем для повтора
            repeat_exam_mode=exam_mode,
            repeat_show_file=show_file
        )
    else:
        await state.update_data(
            repeat_categories=selected_categories,
            repeat_exam_mode=exam_mode,
            repeat_show_file=show_file
        )
    # Статистика
    success_rate = (correct_answers / total_notes * 100) if total_notes > 0 else 0
    
    result_text = (
        f"💡 Экзамен завершен!\n\n"
        f"📊 Результаты:\n"
        f"✅ Правильных ответов: {correct_answers}\n"
        f"❌ Неправильных ответов: {wrong_answers}\n"
        f"📈 Успешность: {success_rate:.1f}%"
    )
    
 
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔄 Повторить экзамен")
    if wrong_notes:  # Показываем кнопку только если есть ошибки
        builder.button(text="🔁 Экзамен по ошибкам")
    builder.button(text="🧩 Меню")
    builder.adjust(2)  # Автоматическое размещение кнопок
    
    finish_keyboard = builder.as_markup(resize_keyboard=True)
    
    await bot.send_message(user_id, result_text, reply_markup=finish_keyboard)
    
    # Показываем карточки с ошибками, если они есть
    if wrong_notes:
        await bot.send_message(user_id, "📝 Карточки, в которых вы ошиблись:")
        
        for note in wrong_notes:
            # Обрезаем длинное название для красоты
            note_title = note.get('content_text', 'Без названия')
            if len(note_title) > 50:
                note_title = note_title[:50] + "..."
                
            # Создаем кнопку для каждой карточки
            show_button = InlineKeyboardButton(
                text="🃏 Показать карточку", 
                callback_data=f"show_wrong_note_{note['id']}"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[show_button]])
            
            await bot.send_message(
                user_id,
                f"❌ {note_title}",
                reply_markup=keyboard
            )
    
    # Устанавливаем состояние завершенного экзамена
    await state.set_state(ExamStates.finished)


@exam_router.message(ExamStates.finished, F.text == "🔁 Экзамен по ошибкам")
async def repeat_wrong_notes_exam(message: Message, state: FSMContext):
    """Повтор экзамена только по карточкам с ошибками."""
    data = await state.get_data()
    wrong_notes = data.get('wrong_notes', [])
    show_file = data.get('repeat_show_file', False)
    
    if not wrong_notes:
        await message.answer("❌ Нет карточек с ошибками для повторения", reply_markup=main_note_kb())
        await state.clear()
        return
    
    # Перемешиваем карточки с ошибками
    random.shuffle(wrong_notes)
    
    await state.update_data(
        exam_notes=wrong_notes,
        current_note_index=0,
        correct_answers=0,
        wrong_answers=0,
        wrong_notes=[],  # очищаем для новой сессии
        exam_mode="wrong_notes",  # новый режим
        show_file=show_file
    )
    
    await message.answer(
        f"🔁 Начинаем экзамен по карточкам с ошибками!\n"
        f"Всего карточек: {len(wrong_notes)}\n"
        f"Показ файла: {'Да' if show_file else 'Нет'}\n\n"
        f"Сосредоточьтесь на этих карточках - они требуют больше внимания!",
        reply_markup=create_stop_exam_keyboard()
    )
    
    await show_next_exam_question(message.from_user.id, state)
    await state.set_state(ExamStates.in_exam)


@exam_router.message(ExamStates.finished, F.text == "🔄 Повторить экзамен")
async def repeat_exam_from_keyboard(message: Message, state: FSMContext):
    """Повтор экзамена с теми же настройками через кнопку клавиатуры."""
    data = await state.get_data()
    selected_categories = data.get('repeat_categories', [])
    show_file = data.get('repeat_show_file', False)
    exam_mode = data.get('repeat_exam_mode', 'normal')
    
    if not selected_categories and exam_mode != 'difficult':
        await message.answer("❌ Нет данных для повторения экзамена",
                             reply_markup=main_mem_kb())
        await state.clear()
        return


    await message.answer("🔄 Запускаю экзамен с теми же настройками...")
    
    if exam_mode == 'difficult':
        # difficult_notes = await get_difficult_notes(user_id=message.from_user.id)
        difficult_notes = data.get('repeat_difficult_notes', [])
        if not difficult_notes:
            difficult_notes = await get_difficult_notes(user_id=message.from_user.id)
        if difficult_notes:
            # Обновляем данные для сложного экзамена
            await state.update_data(
                exam_notes=difficult_notes,
                current_note_index=0,
                correct_answers=0,
                wrong_answers=0,
                wrong_notes=[],
                exam_mode="difficult",
                show_file=show_file
            )
            await show_next_exam_question(message.from_user.id, state)
            await state.set_state(ExamStates.in_exam)
        else:
            await message.answer("❌ Сложные карточки закончились!",
                                 reply_markup=main_note_kb())
            await state.clear()
    else:
        # Запускаем обычный экзамен
        notes = await get_notes_by_categories(
            user_id=message.from_user.id,
            category_ids=selected_categories
        )
        exam_notes = [note for note in notes if note.get('description')]
        
        if not exam_notes:
            await message.answer("❌ В выбранных категориях нет заметок с описанием!",
                                 reply_markup=main_note_kb())
            await state.clear()
            return
            
        random.shuffle(exam_notes)
        
        await state.update_data(
            exam_notes=exam_notes,
            current_note_index=0,
            correct_answers=0,
            wrong_answers=0,
            wrong_notes=[],
            exam_mode="normal",
            show_file=show_file,
            selected_categories=selected_categories
        )
        await show_next_exam_question(message.from_user.id, state)
        await state.set_state(ExamStates.in_exam)


@exam_router.message(ExamStates.finished, F.text == "🧩 Меню")
async def main_menu_from_finished(message: Message, state: FSMContext):
    """Возврат в главное меню после завершения экзамена."""
    await message.answer(
        "Меню мемори:",
        reply_markup=main_mem_kb()
    )
    await state.clear()


@exam_router.callback_query(F.data.startswith('show_wrong_note_'))
async def show_wrong_note(call: CallbackQuery):
    """Показ полной карточки из списка ошибок."""
    note_id = int(call.data.replace('show_wrong_note_', ''))
    
    # Получаем карточку из базы
    from data_base.dao import get_note_by_id
    note = await get_note_by_id(note_id)
    
    if not note:
        await call.answer("❌ Карточка не найдена", show_alert=True)
        return
    
    # Формируем полный текст карточки
    full_card_text = (
        f"📝 Карточка из ошибок:\n\n"
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