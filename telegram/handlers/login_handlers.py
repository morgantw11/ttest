from .start_handlers import start_router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from filters import IsGroupWithOwner
from api_client import DjangoAPIClient
from aiogram.types import Message,ReplyKeyboardRemove
from .start_handlers import show_menu



class SetupStates(StatesGroup):
    waiting_login = State()
    waiting_password = State()


@start_router.message(Command("setup_start"), IsGroupWithOwner)
async def setup_start(message: Message, state: FSMContext):
    await message.answer("🔐 Введите ваш логин от системы:",reply_markup=ReplyKeyboardRemove())
    await state.set_state(SetupStates.waiting_login)

@start_router.message(IsGroupWithOwner, SetupStates.waiting_login)
async def process_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("🔑 Теперь введите ваш пароль:")
    await state.set_state(SetupStates.waiting_password)

@start_router.message(IsGroupWithOwner, SetupStates.waiting_password)
async def process_password(message: Message, state: FSMContext,api_client : DjangoAPIClient):
    user_data = await state.get_data()
    login = user_data.get("login")
    password = message.text

    try:
        success, result = await api_client.login(message.from_user.id, login, password)
        if success:
            user_info = result.get("user", {})
            user_role = user_info.get("role", "user")
            await state.update_data(
                user_role=user_role,
                user_id=user_info.get("id"),
                username=user_info.get("username")
            )
            await show_menu(message,api_client)
        else:
            await message.answer("❌ Ошибка авторизации. Попробуйте снова /setup_start")
    except Exception as e:
        await message.answer(f"❌ Ошибка соединения: {e}")

    await state.clear()