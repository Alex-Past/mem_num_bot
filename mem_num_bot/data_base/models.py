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

    cards: Mapped[List["Card"]] = relationship(
        "Card",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    exams: Mapped[List["Exam"]] = relationship(
        "Exam",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Card(Base):
    """Модель для карточек."""
    __tablename__ = 'cards'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    file_id: Mapped[str] = mapped_column(String, nullable=True)
    value: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='cards')


class Exam(Base):
    """Модель для экзаменов."""
    __tablename__ = 'exams'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='exams')

    cards: Mapped[List["Card"]] = relationship(
        secondary="exam_cards",
        back_populates="exams"
    )


class ExamCard(Base):
    """Промежуточная модель для связи экзаменов и карточек."""
    __tablename__ = 'exam_cards'

    exam_id: Mapped[int] = mapped_column(ForeignKey('exams.id'), primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey('cards.id'), primary_key=True)

    exam: Mapped['Exam'] = relationship(back_populates='cards')
    card: Mapped['Card'] = relationship(back_populates='exams')