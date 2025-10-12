import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, dp, admins
from data_base.base import create_tables
from handlers.memory.random_card_router import random_card_router
from handlers.note.add_cat_router import add_cat_router
from handlers.note.add_note_router import add_note_router
from handlers.note.find_note_router import find_note_router
from handlers.note.find_cat_router import find_cat_router
from handlers.note.upd_note_router import upd_note_router
from handlers.note.view_cat_router import view_cat_router
from handlers.note.upd_cat_router import upd_cat_router
from handlers.start_router import start_router


async def set_commands():
    commands = [
        BotCommand(command='start', description='Старт'),        
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    await set_commands()
    await create_tables()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Бот запущен.')
        except:
            pass


async def stop_bot():
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, 'Бот остановлен.')
        except:
            pass


async def main():
    dp.include_router(start_router)
    dp.include_router(add_note_router)
    dp.include_router(add_cat_router)
    dp.include_router(find_cat_router)
    dp.include_router(find_note_router)
    dp.include_router(view_cat_router)
    dp.include_router(upd_cat_router)
    dp.include_router(upd_note_router)
    dp.include_router(random_card_router)
    
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
