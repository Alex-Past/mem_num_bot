import os

from datetime import datetime

from decouple import config
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import (AsyncAttrs,
                                    async_sessionmaker,
                                    create_async_engine,
                                    AsyncSession)


DATABASE_URL = config('DATABASE_URL')  # Используйте переменную окружения для URL базы данных

if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable not set.")

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс моделей."""
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )