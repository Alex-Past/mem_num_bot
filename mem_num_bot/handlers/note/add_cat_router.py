from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from data_base.dao import add_category
from keyboards.note_kb import (all_category_kb,
                               main_note_kb,
                               add_category_check)


add_cat_router = Router()


class AddNoteStates(StatesGroup):
    category = State()
    check_state_cat = State()


@add_cat_router.message(F.text == "📗 Добавить категорию")
async def start_add_category(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Укажите название категории',
        reply_markup=add_category_check()
    )
    await state.set_state(AddNoteStates.category)


@add_cat_router.message(AddNoteStates.category)
async def handle_category_message(message: Message, state: FSMContext):
    name_text = message.text
    if name_text == '✅ Добавить':
        await message.answer('Укажите название категории')
        await state.set_state(AddNoteStates.category)
    elif name_text == '❌ Отменить':
        await message.answer(
            'Добавление категории отменено!',
            reply_markup=main_note_kb()
        )
        await state.clear()
    elif name_text:
        await state.update_data(category_name=name_text)
        text = (f'⭐️ Название новой категории: "{name_text}". Добавляем?')
        await message.answer(text, reply_markup=add_category_check())
        await state.set_state(AddNoteStates.check_state_cat)


@add_cat_router.message(AddNoteStates.check_state_cat, F.text == "❌ Отменить")
async def cancel_add_category(message: Message, state: FSMContext):
    await message.answer(
        'Добавление категории отменено!',
        reply_markup=main_note_kb()
    )
    await state.clear()


@add_cat_router.message(AddNoteStates.check_state_cat, F.text == "✅ Добавить")
async def confirm_add_category(message: Message, state: FSMContext):
    category = await state.get_data()
    new_category_name = category['category_name']
    new_cat = await add_category(
        user_id=message.from_user.id,
        text_name=new_category_name
    )
    if new_cat is not None:
        await message.answer(
            f'Категория "{new_category_name}" успешно добавлена! 🚀',
            reply_markup=all_category_kb()
        )
    else:
        await message.answer(
            f'Категория "{new_category_name}" уже существует!',
            reply_markup=all_category_kb()
        )
    await state.clear()
