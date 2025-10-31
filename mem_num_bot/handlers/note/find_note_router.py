from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from create_bot import bot
from data_base.dao import get_notes_by_user
from keyboards.note_kb import main_note_kb, find_note_kb
from utils_bot.utils import send_many_notes


find_note_router = Router()


class FindNoteStates(StatesGroup):
    text = State()
    category = State()


@find_note_router.message(F.text == "📒 Просмотр карточек")
async def start_views_noti(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Выбери какие карточки отобразить',
        reply_markup=find_note_kb()
    )


@find_note_router.message(F.text == "🔍 Поиск по тексту")
async def text_views_noti(message: Message, state: FSMContext):
    await state.clear()
    all_notes = await get_notes_by_user(user_id=message.from_user.id)
    if all_notes:
        await message.answer('Введите поисковой запрос.')
        await state.set_state(FindNoteStates.text)
    else:
        await message.answer(
            'У вас пока нет ни одной карточки!',
            reply_markup=main_note_kb()
        )


@find_note_router.message(F.text, FindNoteStates.text)
async def text_noti_process(message: Message, state: FSMContext):
    text_search = message.text.strip()
    all_notes = await get_notes_by_user(
        user_id=message.from_user.id,
        text_search=text_search
    )
    await state.clear()
    if all_notes:
        await message.answer(
            f'📚 C поисковой фразой "{text_search}" '
            f'было обнаружено {len(all_notes)} карточек!',
            reply_markup=main_note_kb()
        )
        await send_many_notes(all_notes, bot, message.from_user.id)
    else:
        await message.answer(
            'У вас пока нет ни одной карточки, '
            f'которая содержала бы в тексте "{text_search}"!',
            reply_markup=main_note_kb()
        )
