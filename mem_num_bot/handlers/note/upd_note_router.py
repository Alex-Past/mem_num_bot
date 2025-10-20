from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from data_base.dao import delete_note_by_id, update_desc_note, update_text_note
from keyboards.note_kb import main_note_kb
from keyboards.other_kb import stop_fsm


upd_note_router = Router()


class UPDNoteStates(StatesGroup):
    content_text = State()
    description_text = State()


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
        f'Название карточки с ID {note_id} успешно изменено на "{content_text}"!',
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
    await state.set_state(UPDNoteStates.description_text)  # Исправлено состояние


# И добавьте отдельный обработчик для состояния описания:
@upd_note_router.message(F.text, UPDNoteStates.description_text)
async def confirm_edit_desc_text(message: Message, state: FSMContext):
    note_data = await state.get_data()
    note_id = note_data.get('note_id')
    description = message.text.strip()
    await update_desc_note(note_id=note_id, description=description)
    await state.clear()
    await message.answer(
        f'Описание карточки с ID {note_id} успешно изменено на "{description}"!',
        reply_markup=main_note_kb()
    )


@upd_note_router.callback_query(F.data.startswith('dell_note_'))
async def dell_note_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    note_id = int(call.data.replace('dell_note_', ''))
    await delete_note_by_id(note_id=note_id)
    await call.answer(f'Карточка удалена!', show_alert=True)
    await call.message.delete()
