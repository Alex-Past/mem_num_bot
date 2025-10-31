from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from data_base.dao import (delete_file_note,
                           delete_note_by_id,
                           get_note_by_id,
                           update_desc_note,
                           update_text_note,
                           update_file_note)
from keyboards.note_kb import main_note_kb, rule_note_kb
from keyboards.other_kb import stop_fsm
from utils_bot.utils import get_content_info  # Импортируем функцию для определения типа контента

upd_note_router = Router()


class UPDNoteStates(StatesGroup):
    content_text = State()
    description_text = State()
    file = State()  # Новое состояние для файла


@upd_note_router.callback_query(F.data.startswith('edit_note_text_'))
async def edit_note_text_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    note_id = int(call.data.replace('edit_note_text_', ''))
    await call.answer(f'✍️ Режим редактирования карточки')
    await state.update_data(note_id=note_id)
    await call.message.answer(
        f'Отправь новое название для этой карточки 👇',
        reply_markup=stop_fsm()
    )
    await state.set_state(UPDNoteStates.content_text)


@upd_note_router.message(F.text, UPDNoteStates.content_text)
async def confirm_edit_note_text(message: Message, state: FSMContext):
    note_data = await state.get_data()
    note_id = note_data.get('note_id')
    content_text = message.text.strip()
    await update_text_note(note_id=note_id, content_text=content_text)
    await state.clear()
    await message.answer(
        f'Название карточки успешно изменено на "{content_text}"!',
        reply_markup=main_note_kb()
    )


@upd_note_router.callback_query(F.data.startswith('edit_desc_text_'))
async def edit_note_desc_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    note_id = int(call.data.replace('edit_desc_text_', ''))
    await call.answer(f'✍️ Режим редактирования описания карточки')
    await state.update_data(note_id=note_id)
    await call.message.answer(
        f'Отправь новое описание для этой карточки 👇',
        reply_markup=stop_fsm()
    )
    await state.set_state(UPDNoteStates.description_text)


@upd_note_router.message(F.text, UPDNoteStates.description_text)
async def confirm_edit_desc_text(message: Message, state: FSMContext):
    note_data = await state.get_data()
    note_id = note_data.get('note_id')
    description = message.text.strip()
    await update_desc_note(note_id=note_id, description=description)
    await state.clear()
    await message.answer(
        f'Описание карточки успешно изменено на "{description}"!',
        reply_markup=main_note_kb()
    )


# Новый обработчик для редактирования файла
@upd_note_router.callback_query(F.data.startswith('edit_file_'))
async def edit_note_file_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    note_id = int(call.data.replace('edit_file_', ''))
    await call.answer(f'✍️ Режим редактирования файла карточки')
    await state.update_data(note_id=note_id)
    await call.message.answer(
        f'Отправь новый файл для этой карточки 👇\n\n'
        f'Можно отправить:\n'
        f'• Фото\n• Видео\n• Документ\n• Аудио\n• Голосовое сообщение'
        f'(подпись не сохранится)',
        reply_markup=stop_fsm()
    )
    await state.set_state(UPDNoteStates.file)


# Обработчик для нового файла
@upd_note_router.message(UPDNoteStates.file)
async def confirm_edit_note_file(message: Message, state: FSMContext):
    note_data = await state.get_data()
    note_id = note_data.get('note_id')
    
    # Используем существующую функцию для определения типа контента
    content_info = get_content_info(message)
    
    if content_info.get('content_type') and content_info.get('file_id'):
        # Обновляем файл в базе данных
        await update_file_note(
            note_id=note_id,
            content_type=content_info['content_type'],
            file_id=content_info['file_id']
        )
        
        await state.clear()
        await message.answer(
            f'Файл карточки успешно изменен!',
            reply_markup=main_note_kb()
        )
    else:
        await message.answer(
            '❌ Я не знаю как работать с таким файлом. '
            'Пожалуйста, отправьте фото, видео, документ,'
            ' аудио или голосовое сообщение.',
            reply_markup=stop_fsm()
        )


@upd_note_router.callback_query(F.data.startswith('dell_note_'))
async def dell_note_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    note_id = int(call.data.replace('dell_note_', ''))
    await delete_note_by_id(note_id=note_id)
    await call.answer(f'Карточка удалена!', show_alert=True)
    await call.message.delete()


# Добавляем новый обработчик для удаления файла
@upd_note_router.callback_query(F.data.startswith('delete_file_'))
async def delete_file_note_process(call: CallbackQuery):
    """Удаление файла из карточки."""
    note_id = int(call.data.replace('delete_file_', ''))
    
    # Удаляем файл из базы данных
    result = await delete_file_note(note_id=note_id)
    
    if result:
        await call.answer("✅ Файл успешно удален из карточки!", show_alert=True)
        
        # Получаем обновленную карточку
        updated_note = await get_note_by_id(note_id)
        
        if updated_note:
            # Формируем текст карточки
            note_text = (f"📝 Карточка обновлена\n\n"
                        f"Категория: {updated_note.get('category_name', 'Без категории')}\n"
                        f"Название: {updated_note.get('content_text', 'Без названия')}\n"
                        f"Описание: {updated_note.get('description', 'Отсутствует')}\n"
                        f"Файл: {'Отсутствует' if not updated_note.get('file_id') else 'Есть'}")
            
            # Обновляем сообщение с новой клавиатурой (без кнопки удаления файла)
            await call.message.edit_text(
                text=note_text,
                reply_markup=rule_note_kb(note_id, has_file=False)
            )
        else:
            await call.answer("❌ Ошибка при получении данных карточки", show_alert=True)
    else:
        await call.answer("❌ Не удалось удалить файл", show_alert=True)    