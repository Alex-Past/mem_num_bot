from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from data_base.dao import delete_category, update_category
from keyboards.note_kb import all_category_kb, del_check, main_note_kb
from keyboards.other_kb import stop_fsm


upd_cat_router = Router()


class UPDNoteStates(StatesGroup):
    text = State()
    check_state = State()


@upd_cat_router.callback_query(F.data.startswith('edit_cat_text_'))
async def edit_cat_text_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    cat_id = int(call.data.replace('edit_cat_text_', ''))
    await call.answer(f'✍️ Режим редактирования категории')
    await state.update_data(cat_id=cat_id)
    await call.message.answer(
        'Введи новое название категории 👇',
        reply_markup=stop_fsm()
    )
    await state.set_state(UPDNoteStates.text)


@upd_cat_router.message(F.text, UPDNoteStates.text)
async def confirm_edit_cat_text(message: Message, state: FSMContext):
    cat_data = await state.get_data()
    cat_id = cat_data.get('cat_id')
    text = message.text.strip()
    await update_category(category_id=cat_id, text_name=text)
    await state.clear()
    await message.answer(
        f'Название категории успешно изменен на "{text}"!',
        reply_markup=main_note_kb()
    )


@upd_cat_router.callback_query(F.data.startswith('dell_cat_'))
async def dell_check_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    category_id = call.data.replace('dell_cat_', '')
    await state.update_data(category_id=category_id)
    await call.message.answer(
        f'Все карточки этой категории будут удалены!',
        reply_markup=del_check()
    )
    await state.set_state(UPDNoteStates.check_state)


@upd_cat_router.message(UPDNoteStates.check_state, F.text == "🗑 Удалить")
async def dell_cat_process(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = int(data.get('category_id'))
    await delete_category(category_id=category_id)
    await message.answer(
        f'Категория удалена!',
        reply_markup=all_category_kb()
    )
    await state.clear()


@upd_cat_router.message(UPDNoteStates.check_state, F.text == "❌ Отменить")
async def cancel_del_cat(message: Message, state: FSMContext):
    await message.answer('Удаление отменено!', reply_markup=all_category_kb())
    await state.clear()
