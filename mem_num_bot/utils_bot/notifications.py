import asyncio
from datetime import datetime, time
from aiogram import Bot
from data_base.dao import get_difficult_notes
from keyboards.note_kb import main_note_kb

class NotificationManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_users = set()  # user_id пользователей с включенными уведомлениями
        self.is_running = False

    def add_user(self, user_id: int):
        """Добавляем пользователя в список для уведомлений."""
        self.active_users.add(user_id)

    def remove_user(self, user_id: int):
        """Удаляем пользователя из списка уведомлений."""
        self.active_users.discard(user_id)

    def is_user_active(self, user_id: int) -> bool:
        """Проверяем, включены ли уведомления для пользователя."""
        return user_id in self.active_users

    async def start(self):
        """Запускаем фоновую задачу для проверки уведомлений."""
        if self.is_running:
            return
        
        self.is_running = True
        asyncio.create_task(self._notification_worker())

    async def _notification_worker(self):
        """Фоновая задача для отправки уведомлений."""
        while self.is_running:
            try:
                now = datetime.now().time()
                
                # Проверяем, 20:00 ли сейчас (с допуском ±1 минута)
                target_time = time(20, 0)
                current_time = time(now.hour, now.minute)
                
                if (target_time.hour == current_time.hour and 
                    abs(target_time.minute - current_time.minute) <= 1):
                    
                    await self._send_difficult_notes_notifications()
                    
                    # Ждем 2 минуты, чтобы не отправлять повторно
                    await asyncio.sleep(120)
                else:
                    # Проверяем каждую минуту
                    await asyncio.sleep(60)
                    
            except Exception as e:
                print(f"Ошибка в notification_worker: {e}")
                await asyncio.sleep(60)

    async def _send_difficult_notes_notifications(self):
        """Отправляем уведомления о сложных карточках."""
        for user_id in list(self.active_users):
            try:
                difficult_notes = await get_difficult_notes(user_id=user_id)
                
                if difficult_notes:
                    await self.bot.send_message(
                        user_id,
                        f"📚 У вас накопилось {len(difficult_notes)} карточек, "
                        f"которые запоминаются хуже всего.\n\n"
                        f"Перейдите в раздел 'Экзамен' → 'Повторить сложные' "
                        f"и изучите их повторно.",
                        reply_markup=main_note_kb()
                    )
                    
            except Exception as e:
                print(f"Не удалось отправить уведомление пользователю {user_id}: {e}")

# Глобальный экземпляр менеджера уведомлений
notification_manager = None

def setup_notifications(bot: Bot):
    """Инициализация менеджера уведомлений."""
    global notification_manager
    notification_manager = NotificationManager(bot)
    return notification_manager