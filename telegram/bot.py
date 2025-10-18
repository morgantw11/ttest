import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from api_client import DjangoAPIClient
from handlers.start_handlers import start_router
from aiogram3_di import setup_di
import os
from session_error import SessionErrorMiddleware

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
TELEGRAM_BOT_SECRET = os.getenv("TELEGRAM_BOT_SECRET")
ID_OWNER = os.getenv("ID_OWNER")

#DjangoAPIClient(API_BASE_URL, TELEGRAM_BOT_SECRET)
# Конфигурация

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage,api_client = DjangoAPIClient(API_BASE_URL, TELEGRAM_BOT_SECRET))
dp.include_router(start_router)
dp.message.middleware(SessionErrorMiddleware())
dp.callback_query.middleware(SessionErrorMiddleware())

setup_di(dp)


async def main():
    print("Бот запущен! 🚀")
    await dp.start_polling(bot )

if __name__ == "__main__":
    asyncio.run(main())