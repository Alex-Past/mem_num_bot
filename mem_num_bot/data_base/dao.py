from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional

from create_bot import logger
from .base import connection
from .models import Category, User, Note


@connection
async def set_user(
    session,
    tg_id: int,
    username: str,
    full_name: str
) -> Optional[User]:
    """Создаем пользователя, если его нет."""
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))

        if not user:
            new_user = User(id=tg_id, username=username, full_name=full_name)
            session.add(new_user)
            await session.commit()
            logger.info(f"Зарегистрировал пользователя с ID {tg_id}!")
            return None
        else:
            logger.info(f"Пользователь с ID {tg_id} найден!")
            return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        await session.rollback()


@connection
async def add_category(
    session,
    user_id: int,
    text_name: str,
) -> Optional[Category]:
    """Создаем категорию."""
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))
        if not user:
            logger.error(f"Пользователь с ID {user_id} не найден.")
            return None
        category = await session.scalar(select(Category).filter_by(
            name=text_name,
            user_id=user_id
        ))
        if not category:
            new_category = Category(
                name=text_name,
                user_id=user_id
            )
            session.add(new_category)
            await session.commit()
            logger.info(f"Добавлена новая категория: {text_name}!")
            return new_category
        else:
            logger.info(f"Категория {text_name} уже существует!")
            return None
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении категории: {e}")
        await session.rollback()


@connection
async def update_category(
    session,
    category_id: int,
    text_name: str
) -> Optional[Note]:
    """Обновляем название категории."""
    try:
        category = await session.get(Category, category_id)
        if not category:
            logger.error(f"Категория '{text_name}' не найдена.")
            return None

        category.name = text_name
        await session.commit()
        logger.info(f"Категория '{text_name}' успешно обновлена!")
        return category
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении категории: {e}")
        await session.rollback()


@connection
async def delete_category(
    session,
    category_id: int,    
) -> Optional[Note]:
    """Удаляем категорию."""
    try:
        category = await session.get(Category, category_id)
        if not category:
            logger.error(f"Категория с ID {category_id} не найдена.")                        
            return None 

        await session.delete(category)
        await session.commit()
        logger.info(f"Заметка с ID {category_id} успешно удалена.")
        return category
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении заметки: {e}")
        await session.rollback()
        return None


@connection
async def get_all_categories(
    session,
    # user_id: int,
    text_search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Получаем список всех категорий пользователя."""
    try:
        stmt = select(Category)#.filter_by(user_id=user_id)
        result = await session.execute(stmt)
        categories = result.scalars().all()
        if not categories:
            logger.info("Категории не найдены.")
            return []

        cat_list = [
            {
                'id': cat.id,
                'category_name': cat.name
            } for cat in categories
        ]

        if text_search:
            cat_list = [
                note for note in cat_list
                if text_search.lower() in (
                    note['category_name'] or ''
                ).lower()
            ]

        return cat_list

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении категорий: {e}")
        return []


@connection
async def get_category_by_id(
    session,
    cat_id: int
) -> Optional[Dict[str, Any]]:
    """Получаем категорию по ID."""
    try:
        stmt = select(Category).where(Category.id == cat_id)
        category = await session.scalar(stmt)
        if not category:
            logger.info(f"Категория с ID {cat_id} не найдена.")
            return None

        return {
            'id': category.id,
            'category_name': category.name
        }
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении категории: {e}")
        return None


@connection
async def add_note(
    session,
    user_id: int,
    content_type: str,
    category_id: int,
    content_text: Optional[str] = None,
    description: Optional[str] = None,
    file_id: Optional[str] = None
) -> Optional[Note]:
    """Создаем заметку."""
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))
        if not user:
            logger.error(f"Пользователь с ID {user_id} не найден.")
            return None

        new_note = Note(
            user_id=user_id,
            content_type=content_type,
            category_id=category_id,
            content_text=content_text,
            description=description,
            file_id=file_id
        )

        session.add(new_note)
        await session.commit()
        logger.info(
            f"Заметка для пользователя с ID {user_id} успешно добавлена!")
        return new_note
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении заметки: {e}")
        await session.rollback()


@connection
async def update_text_note(
    session,
    note_id: int,
    content_text: str
) -> Optional[Note]:
    """Обновляем текст заметки."""
    try:
        note = await session.scalar(select(Note).filter_by(id=note_id))
        if not note:
            logger.error(f"Заметка с ID {note_id} не найдена.")
            return None

        note.content_text = content_text
        await session.commit()
        logger.info(f"Заметка с ID {note_id} успешно обновлена!")
        return note
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении заметки: {e}")
        await session.rollback()


@connection
async def update_desc_note(
    session,
    note_id: int,
    description: str
) -> Optional[Note]:
    """Обновляем текст заметки."""
    try:
        note = await session.scalar(select(Note).filter_by(id=note_id))
        if not note:
            logger.error(f"Заметка с ID {note_id} не найдена.")
            return None

        note.description = description
        await session.commit()
        logger.info(f"Заметка с ID {note_id} успешно обновлена!")
        return note
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении заметки: {e}")
        await session.rollback()


@connection
async def get_note_by_id(session, note_id: int) -> Optional[Dict[str, Any]]:
    """Получаем заметку по ID."""
    try:
        stmt = select(Note).options(
            selectinload(Note.category)
        ).where(Note.id == note_id)
        result = await session.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            logger.info(f"Заметка с ID {note_id} не найдена.")
            return None

        return {
            'id': note.id,
            'category_name': note.category.name,
            'content_type': note.content_type,
            'content_text': note.content_text,
            'description': note.description,
            'file_id': note.file_id
        }
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении заметки: {e}")
        return None


@connection
async def delete_note_by_id(session, note_id: int) -> Optional[Note]:
    """Удаляем заметку."""
    try:
        note = await session.get(Note, note_id)
        if not note:
            logger.error(f"Заметка с ID {note_id} не найдена.")
            return None

        await session.delete(note)
        await session.commit()
        logger.info(f"Заметка с ID {note_id} успешно удалена.")
        return note
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении заметки: {e}")
        await session.rollback()
        return None


@connection
async def get_notes_by_user(
    session,
    # user_id: int,
    text_search: Optional[str] = None,
    category_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Получаем заметки пользователя."""
    try:
        stmt = select(Note)#.filter(Note.user_id == user_id)

        if category_id is not None:
            stmt = stmt.filter(Note.category_id == category_id)

        result = await session.execute(stmt)
        notes = result.scalars().all()

        if not notes:
            logger.info("Заметки не найдены.")
            return []

        note_list = [
            {
                'id': note.id,
                'created_at': note.created_at,
                'content_type': note.content_type,
                'content_text': note.content_text,
                'description': note.description,
                'file_id': note.file_id,
                'category_id': note.category_id,
            } for note in notes
        ]

        if text_search:
            note_list = [
                note for note in note_list
                if text_search.lower() in (note['content_text'] or '').lower()
            ]

        return note_list

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении заметок: {e}")
        return []


@connection
async def find_notes_by_category_name(
    session,
    category_name: str
) -> List[Dict[str, Any]]:
    """Поиск заметок по имени категории."""
    try:
        stmt = (
            select(Note)
            .join(Category)
            .where(Category.name == category_name)
            .options(selectinload(Note.category))
        )

        result = await session.execute(stmt)
        notes = result.scalars().all()

        if not notes:
            logger.info(
                f"Заметки для категории '{category_name}' не найдены."
            )
            return []

        notes_list = [
            {
                'id': note.id,
                'created_at': note.created_at,
                'content_type': note.content_type,
                'content_text': note.content_text,
                'description': note.description,
                'file_id': note.file_id,
                'category_id': note.category_id,
                'category_name': note.category.name
            } for note in notes
        ]

        return notes_list

    except SQLAlchemyError as e:
        logger.error(
            f"Ошибка при поиске заметок по категории '{category_name}': {e}"
        )
        return []


@connection
async def get_notes_count(session, user_id: int) -> int:
    """Получаем количество заметок пользователя."""
    try:
        stmt = select(Note).filter(Note.user_id == user_id)
        result = await session.execute(stmt)
        notes = result.scalars().all()
        return len(notes)
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении количества заметок: {e}")
        return 0

@connection
async def get_random_note(session, user_id: int) -> Optional[Dict[str, Any]]:
    """Получаем случайную заметку пользователя."""
    try:
        # Получаем все заметки пользователя
        stmt = select(Note).filter(Note.user_id == user_id)
        result = await session.execute(stmt)
        notes = result.scalars().all()
        
        if not notes:
            return None
            
        # Выбираем случайную заметку
        import random
        random_note = random.choice(notes)
        
        # Загружаем связанную категорию
        await session.refresh(random_note, ['category'])
        
        # Получаем название категории
        category_name = "Без категории"
        if random_note.category:
            category_name = random_note.category.name
            
        return {
            'id': random_note.id,
            'category_name': category_name,
            'content_type': random_note.content_type,
            'content_text': random_note.content_text,
            'description': random_note.description,
            'file_id': random_note.file_id
        }
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении случайной заметки: {e}")
        return None