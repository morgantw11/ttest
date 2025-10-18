from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
import os

ID_OWNER = os.getenv("ID_OWNER")
class IsGroupWithOwnerFilter(BaseFilter):
    def __init__(self, owner_id: int):
        self.owner_id = owner_id
    
    async def __call__(self, message_or_callback: Message | CallbackQuery, bot) -> bool:
        # Определяем чат в зависимости от типа
        if isinstance(message_or_callback, Message):
            chat = message_or_callback.chat
        else:
            chat = message_or_callback.message.chat
        
        # Проверяем, что это не личка
        if chat.type == "private":
            return False

        # Проверяем, что OWNER есть в группе
        try:
            member = await bot.get_chat_member(chat.id, self.owner_id)
            return member.status in ["member", "administrator", "creator"]
        except:
            return False

# Создаем экземпляр фильтра
IsGroupWithOwner = IsGroupWithOwnerFilter(owner_id=ID_OWNER)