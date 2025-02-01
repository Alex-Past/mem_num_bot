import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, dp, admins
from data_base.base import init_database


async def set_commands():
    commands = [
        BotCommand(command='start', description='Старт'),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    await set_commands()
    await init_database()  # Инициализируем базу данных
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
    # dp.include_router(start_router)

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
