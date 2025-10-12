from sqlalchemy import BigInteger, Integer, Text, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional

from .database import Base


class User(Base):
    """Модель для таблицы пользователей."""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    notes: Mapped[List["Note"]] = relationship(
        "Note",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Category(Base):
    """Модель для таблицы категорий."""
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="Общее"
    )

    user: Mapped["User"] = relationship("User", back_populates="categories")
    notes: Mapped[List["Note"]] = relationship(
        "Note",
        back_populates="category",
        cascade="all, delete-orphan"
    )


class Note(Base):
    """Модель для таблицы заметок."""
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('categories.id'),
        nullable=True
    )
    content_type: Mapped[str] = mapped_column(String, nullable=True)
    content_text: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    file_id: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notes")
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="notes"
    )
