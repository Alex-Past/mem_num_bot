from .database import async_session, engine, Base


def connection(func):
    """Декоратор для подключения к базе данных."""
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper


async def create_tables():
    """Создаем БД."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)