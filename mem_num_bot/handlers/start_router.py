from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from decouple import config

from data_base.dao import set_user
from keyboards.other_kb import main_kb
from keyboards.note_kb import main_note_kb
from keyboards.mem_kb import main_mem_kb

SPACE=config("SPACE")

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Пожалуйста, введите код:")

@start_router.message(F.text == SPACE)
async def process_check_space(message: Message):    
    await set_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    greeting = (
        f'Привет, {message.from_user.username}! '
        'Выбери необходимое действие'
    )
    await message.answer(greeting, reply_markup=main_kb())


@start_router.message(F.text == "🏠 Главное меню")
async def mine_menu(message: Message, state: FSMContext):
    await state.clear()
    greeting = 'Вы в главном меню. Выбери необходимое действие'
    await message.answer(greeting, reply_markup=main_kb())


@start_router.message(F.text == "🧩 Мемори")
async def mine_menu(message: Message, state: FSMContext):
    await state.clear()
    greeting = 'Вы в модуле для запоминания карточек. Выбери необходимое действие'
    await message.answer(greeting, reply_markup=main_mem_kb())


@start_router.message(F.text == "❌ Отмена")
async def stop_fsm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Сценарий остановлен. '
        'Для выбора действия воспользуйся клавиатурой ниже',
        reply_markup=main_note_kb()
    )

@start_router.callback_query(F.data == 'main_menu')
async def main_menu_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Вы вернулись в главное меню.')
    await call.message.answer(
        f'Привет, {call.from_user.full_name}! '
        'Выбери необходимое действие',
        reply_markup=main_kb()
    )
