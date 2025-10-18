from aiogram import BaseMiddleware
from aiogram.types import Update

from api_client import SessionExpiredError


class SessionErrorMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        try:
            return await handler(event, data)
        except SessionExpiredError:
            # Универсально отвечаем пользователю
            if hasattr(event, "message") and event.message:
                await event.message.answer("⚠️ Ваша сессия истекла. Пожалуйста, войдите заново. /setup_start")
            elif hasattr(event, "callback_query") and event.callback_query:
                await event.callback_query.message.answer("⚠️ Ваша сессия истекла. Пожалуйста, войдите заново.")
            # Возвращаем None, чтобы ошибка не улетела дальше
            return None
