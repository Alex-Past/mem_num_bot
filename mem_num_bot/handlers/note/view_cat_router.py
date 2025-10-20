from aiogram import Router, F
from aiogram.types import Message

from create_bot import bot
from data_base.dao import get_all_categories
from keyboards.note_kb import all_category_kb
from utils_bot.utils import send_many_categories


view_cat_router = Router()


@view_cat_router.message(F.text == "📋 Список категорий")
async def all_views_category(message: Message):
    all_category = await get_all_categories(user_id=message.from_user.id)
    if all_category:
        await message.answer(
            f'⭐️ Найдено всего {len(all_category)} категорий',
            reply_markup=all_category_kb()
        )
        await send_many_categories(all_category, bot, message.from_user.id)
    else:
        await message.answer(
            'У вас пока нет ни одной категории!',
            reply_markup=all_category_kb()
        )
