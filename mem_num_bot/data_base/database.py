from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import (AsyncAttrs,
                                    async_sessionmaker,
                                    create_async_engine,
                                    AsyncSession)


# engine = create_async_engine(url='sqlite+aiosqlite:///data/db.sqlite3')

import os

# Покажите какой путь используете
db_path = "/data/db.sqlite3"  # или ваш текущий путь

engine = create_async_engine(url=f'sqlite+aiosqlite:///{db_path}')
async_session = async_sessionmaker(engine, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс моделей."""
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )