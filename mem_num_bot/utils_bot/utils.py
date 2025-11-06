import asyncio
from aiogram.types import Message

from create_bot import admins
from keyboards.note_kb import rule_cat_kb, rule_note_kb
from data_base.dao import get_category_by_id


def get_content_info(message: Message):
    content_type = None
    file_id = None

    if message.photo:
        content_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        content_type = "video"
        file_id = message.video.file_id
    elif message.audio:
        content_type = "audio"
        file_id = message.audio.file_id
    elif message.document:
        content_type = "document"
        file_id = message.document.file_id
    elif message.voice:
        content_type = "voice"
        file_id = message.voice.file_id
    elif message.text:
        content_type = "text"

    content_text = message.text or message.caption
    return {
        'content_type': content_type,
        'file_id': file_id,
        'content_text': content_text
    }


async def send_message_user(bot, content_type, content_text, user_id, file_id=None, kb=None):
    """Отправляет сообщение пользователю с возможными медиафайлами."""
    try:
        # Проверяем, что user_id не является ID бота
        if str(user_id).startswith('0') or len(str(user_id)) < 8:
            print(f"❌ Некорректный user_id: {user_id}")
            return None
            
        # Обрезаем текст если он слишком длинный для подписи
        if content_type != "text" and file_id and len(content_text) > 1024:
            content_text = content_text[:1020] + "..."

        if content_type == "photo" and file_id:
            message = await bot.send_photo(
                chat_id=user_id,
                photo=file_id,
                caption=content_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return message.message_id
        elif content_type == "video" and file_id:
            message = await bot.send_video(
                chat_id=user_id,
                video=file_id,
                caption=content_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return message.message_id
        elif content_type == "audio" and file_id:
            message = await bot.send_audio(
                chat_id=user_id,
                audio=file_id,
                caption=content_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return message.message_id
        elif content_type == "document" and file_id:
            message = await bot.send_document(
                chat_id=user_id,
                document=file_id,
                caption=content_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return message.message_id
        elif content_type == "voice" and file_id:
            message = await bot.send_voice(
                chat_id=user_id,
                voice=file_id,
                caption=content_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return message.message_id
        else:
            # Если тип контента не поддерживается или файл отсутствует, отправляем текст
            message = await bot.send_message(
                chat_id=user_id,
                text=content_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return message.message_id
    except Exception as e:
        print(f"❌ Ошибка в send_message_user: {e}")
        print(f"   user_id: {user_id}, content_type: {content_type}, file_id: {file_id}")
        
        # В случае ошибки отправляем просто текстовое сообщение
        try:
            message = await bot.send_message(
                chat_id=user_id,
                text=content_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return message.message_id
        except Exception as e2:
            print(f"❌ Критическая ошибка при отправке текста: {e2}")
            return None


async def send_many_notes(all_notes, bot, user_id):
    """Функция для отправки списка заметок."""
    for note in all_notes:        
        # Определяем, есть ли файл у заметки
        has_file = bool(note.get('file_id') and note.get('content_type') != 'text')
        
        # Передаем параметр has_file в клавиатуру
        kb = rule_note_kb(note['id'], has_file=has_file)
         
        try:
            category = await get_category_by_id(note['category_id'])
            cat_name = category['category_name']
            text = (f"{note['created_at'].strftime('%d-%m-%Y')}\n"
                    f"✨ Категория: <u>{cat_name if cat_name else ''}</u>\n\n"
                    f"<b>{note['content_text'] if note['content_text'] else 'Без названия'}</b>\n\n"
                    f"<b>{note['description'] if note['description'] else 'Без описания'}</b>\n\n"
                    "📚")
            await send_message_user(
                bot=bot,
                content_type=note['content_type'],
                content_text=text,
                user_id=user_id,
                file_id=note['file_id'],
                kb=kb                
            )
        except Exception as e:
            print(f'Error: {e}')
            await asyncio.sleep(2)
        finally:
            await asyncio.sleep(0.2)


async def send_many_categories(all_category, bot, user_id):
    """Функция для отправки списка категорий."""
    for category in all_category:
        # if user_id in admins:
        #     reply_markup=rule_cat_kb(category['id'])
        # else:
        #     reply_markup = None
        try:
            text = f"✨ Категория: <b>{category['category_name']}</b>\n\n"
            await bot.send_message(
                text=text,
                chat_id=user_id,
                # reply_markup=reply_markup
                reply_markup=rule_cat_kb(category['id'])
            )
        except Exception as e:
            print(f'Error: {e}')
            await asyncio.sleep(2)
        finally:
            await asyncio.sleep(0.2)
