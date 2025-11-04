from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
import asyncio

from data_base.dao import get_total_users_count, get_all_users
from keyboards.admin_kb import admin_main_kb
from create_bot import bot, admins
from keyboards.other_kb import main_kb


admin_router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()

@admin_router.message(F.text == 'admin')
async def mine_menu_admin(message: Message, state: FSMContext):
    await state.clear()
    user_id=message.from_user.id
    if user_id in admins:
        greeting = 'Вы в меню для администраторов. Выбери необходимое действие'
        await message.answer(greeting, reply_markup=admin_main_kb())
    else:
        greeting = 'Этот раздел только для администратора.'
        await message.answer(greeting, reply_markup=main_kb())


# Обработчик кнопки "Пользователи"
@admin_router.message(F.text == "Пользователи")
async def show_users_count(message: Message):
    count = await get_total_users_count()
    await message.answer(f"📊 Всего пользователей: {count}", reply_markup=admin_main_kb())


# Обработчик кнопки "Рассылка"
@admin_router.message(F.text == "Рассылка")
async def start_broadcast(message: Message, state: FSMContext):
    await message.answer(
        "Введите сообщение для рассылки, только текст!!!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AdminStates.waiting_for_broadcast_message)


# Обработчик сообщения для рассылки
@admin_router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    broadcast_text = message.text
    users = await get_all_users()
    
    if not users:
        await message.answer("❌ Нет пользователей для рассылки", reply_markup=admin_main_kb())
        await state.clear()
        return
    
    # Отправляем подтверждение
    confirm_message = await message.answer(
        f"📤 Начинаю рассылку для {len(users)} пользователей...\n\n"
        f"Сообщение: {broadcast_text}"
    )
    
    # Рассылаем сообщения
    success_count = 0
    fail_count = 0
    
    for user_id in users:
        try:
            await bot.send_message(user_id, broadcast_text)
            success_count += 1
            # Небольшая задержка чтобы не спамить
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            fail_count += 1
    
    # Отправляем результат
    await confirm_message.edit_text(
        f"✅ Рассылка завершена!\n\n"
        f"📊 Результаты:\n"
        f"✅ Успешно: {success_count}\n"
        f"❌ Не удалось: {fail_count}\n"
        f"👥 Всего: {len(users)}"
    )
    
    await message.answer("Админ-панель:", reply_markup=admin_main_kb())
    await state.clear()
