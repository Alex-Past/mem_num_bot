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


async def send_message_user(
    bot, user_id,
    content_type,
    content_text=None,
    file_id=None,
    kb=None
):
    """Отправляем сообщение, в зависимости от контента."""
    match content_type:
        case 'text': await bot.send_message(
            chat_id=user_id,
            text=content_text,
            reply_markup=kb
        )
        case 'photo': await bot.send_photo(
            chat_id=user_id,
            photo=file_id,
            caption=content_text,
            reply_markup=kb
        )
        case 'document': await bot.send_document(
            chat_id=user_id,
            document=file_id,
            caption=content_text,
            reply_markup=kb
        )
        case 'video': await bot.send_video(
            chat_id=user_id,
            video=file_id,
            caption=content_text,
            reply_markup=kb
        )
        case 'audio': await bot.send_audio(
            chat_id=user_id,
            audio=file_id,
            caption=content_text,
            reply_markup=kb
        )
        case 'voice': await bot.send_voice(
            chat_id=user_id,
            voice=file_id,
            caption=content_text,
            reply_markup=kb
        )


async def send_many_notes(all_notes, bot, user_id):
    """Функция для отправки списка заметок."""
    for note in all_notes:        
        kb = rule_note_kb(note['id'])         
        try:
            category = await get_category_by_id(note['category_id'])
            cat_name = category['category_name']
            text = (f"{note['created_at'].strftime('%d-%m-%Y')}\n"
                    f"✨ Категория: <u>{cat_name if cat_name else ''}</u>\n\n"
                    f"<b>{note['content_text'] if note['content_text'] else ''}</b>\n\n"
                    f"<b>{note['description'] if note['description'] else ''}</b>\n\n"
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
        if user_id in admins:
            reply_markup=rule_cat_kb(category['id'])
        else:
            reply_markup = None
        try:
            text = f"✨ Категория: <b>{category['category_name']}</b>\n\n"
            await bot.send_message(
                text=text,
                chat_id=user_id,
                reply_markup=reply_markup
                # reply_markup=rule_cat_kb(category['id'])
            )
        except Exception as e:
            print(f'Error: {e}')
            await asyncio.sleep(2)
        finally:
            await asyncio.sleep(0.2)
