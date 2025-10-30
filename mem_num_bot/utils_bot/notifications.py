import asyncio
from datetime import datetime, time
from aiogram import Bot
from data_base.dao import get_difficult_notes
from keyboards.note_kb import main_note_kb

class NotificationManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_users = set()  # user_id пользователей с включенными уведомлениями
        self.user_notification_times = {}  # user_id -> время в формате "HH:MM"
        self.is_running = False

    def add_user(self, user_id: int, notification_time: str = "20:00"):
        """Добавляем пользователя в список для уведомлений."""
        self.active_users.add(user_id)
        if user_id not in self.user_notification_times:
            self.user_notification_times[user_id] = notification_time

    def remove_user(self, user_id: int):
        """Удаляем пользователя из списка уведомлений."""
        self.active_users.discard(user_id)

    def set_user_notification_time(self, user_id: int, time_str: str):
        """Устанавливаем время уведомлений для пользователя."""
        self.user_notification_times[user_id] = time_str
        # Автоматически включаем уведомления при установке времени
        self.active_users.add(user_id)

    def get_user_notification_time(self, user_id: int) -> str:
        """Получаем время уведомлений для пользователя."""
        return self.user_notification_times.get(user_id, "20:00")

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
                now = datetime.now()
                current_time_str = now.strftime("%H:%M")
                
                # Проверяем для каждого пользователя его время
                for user_id in list(self.active_users):
                    user_time = self.user_notification_times.get(user_id, "20:00")
                    
                    # Проверяем совпадение времени (с допуском ±1 минута)
                    if self._is_time_match(current_time_str, user_time):
                        await self._send_difficult_notes_notifications(user_id)
                
                # Ждем 60 секунд перед следующей проверкой
                await asyncio.sleep(60)
                    
            except Exception as e:
                print(f"Ошибка в notification_worker: {e}")
                await asyncio.sleep(60)

    def _is_time_match(self, current_time: str, target_time: str) -> bool:
        """Проверяет, совпадает ли текущее время с целевым (с допуском ±1 минута)."""
        try:
            current = datetime.strptime(current_time, "%H:%M")
            target = datetime.strptime(target_time, "%H:%M")
            
            # Вычисляем разницу в минутах
            time_diff = abs((current - target).total_seconds() / 60)
            
            return time_diff <= 1
        except ValueError:
            return False

    async def _send_difficult_notes_notifications(self, user_id: int):
        """Отправляем уведомления о сложных карточках конкретному пользователю."""
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
                print(f"✅ Отправлено уведомление пользователю {user_id} о {len(difficult_notes)} сложных карточках")
            else:
                print(f"ℹ️ У пользователя {user_id} нет сложных карточек для уведомления")
                
        except Exception as e:
            print(f"❌ Не удалось отправить уведомление пользователю {user_id}: {e}")

# Глобальный экземпляр менеджера уведомлений
notification_manager = None

def setup_notifications(bot: Bot):
    """Инициализация менеджера уведомлений."""
    global notification_manager
    notification_manager = NotificationManager(bot)
    return notification_manager