from .start_handlers import start_router
from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from filters import IsGroupWithOwner
from api_client import DjangoAPIClient
from .utils import generate_password

class CreateUserStates(StatesGroup):
    waiting_username = State()
    waiting_big_text = State()
    waiting_file_name = State()
    waiting_password = State()
    waiting_role = State()


@start_router.message(IsGroupWithOwner, F.text == "🙋‍♂️ Добавить пользователя")
async def create_user_start(message: Message, state: FSMContext, api_client: DjangoAPIClient):
    await message.answer("Введите EMAIL нового пользователя:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateUserStates.waiting_username)
    
@start_router.message(IsGroupWithOwner, CreateUserStates.waiting_username)
async def create_user_username(message: Message, state: FSMContext):
    await state.update_data(new_username=message.text)
    await message.answer("Введите имя создателя файла:")
    await state.set_state(CreateUserStates.waiting_big_text)



@start_router.message(IsGroupWithOwner, CreateUserStates.waiting_big_text)
async def create_user_big_text(message: Message, state: FSMContext):
    await state.update_data(big_text=message.text or "")
    await message.answer("Введите название файла для скачивания:")
    await state.set_state(CreateUserStates.waiting_file_name)

@start_router.message(IsGroupWithOwner, CreateUserStates.waiting_file_name)
async def create_user_file_name(message: Message, state: FSMContext):
    await state.update_data(file_name=message.text or "")
    
    # Генерация кнопки InlineKeyboard для пароля
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сгенерировать пароль", callback_data="generate_password")]
        ]
    )
    await message.answer("Введите пароль нового пользователя:", reply_markup=keyboard)
    await state.set_state(CreateUserStates.waiting_password)


@start_router.callback_query(F.data == "generate_password")
async def generate_password_callback(callback: CallbackQuery, state: FSMContext):
    password = generate_password()
    await state.update_data(generated_password=password)
    await callback.message.edit_text(f"Сгенерированный пароль: `{password}`", parse_mode="Markdown")
    await callback.answer("Пароль сгенерирован. Можете скопировать его в поле ввода.")


async def create_user_finalize(message: Message, state: FSMContext, api_client: DjangoAPIClient):
    data = await state.get_data()
    chat_id = message.chat.id
    payload = {
        "username": data["new_username"],
        "password": data["password"],
        "role": data.get("role", "user"),
        "big_text": data.get("big_text", ""),
        "file_name": data.get("file_name", ""),
        "telegram_group_id":chat_id
    }

    response_data, status = await api_client.post(message.from_user.id, "api/users/create/", json=payload)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Выйти в главное меню")]],
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню'
    )

    if status == 201:
        inline_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=f"👤 {payload['username']}", callback_data=f"user_{response_data.get('id')}")],
                ]
        )
        user_role = data.get("role","user")
        
        if user_role == "user":
            user_id = response_data.get('id')

            magic_payload = {"user_id":user_id}
            magic_data, magic_status = await api_client.post(message.from_user.id,"api/magic-link/create/",json=magic_payload)

            if magic_status == 201:
                magic_link = magic_data.get("magic_link")
                await message.answer(
                    f"✅ Пользователь создан! \n Его ссылка входа `{magic_link}` ",
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                    reply_markup=inline_keyboard
                )
            else:
                await message.answer(
                    f"✅ Пользователь создан! Но не получилось сгенерировать ссылку, напишите админу",
                    reply_markup=inline_keyboard
                )
        else:
            await message.answer(
                f"✅ Рабочий пользователь создан!",
                reply_markup=inline_keyboard
            )
                
                        
        await message.answer("Для большой информации нажмите на кнопку выше", reply_markup=keyboard)

    else:
        await message.answer(f"❌ Ошибка при создании пользователя:\n{response_data}", reply_markup=keyboard)

    await state.clear()




@start_router.message(IsGroupWithOwner, CreateUserStates.waiting_password)
async def create_user_password(message: Message, state: FSMContext, api_client: DjangoAPIClient):
    user_data = await state.get_data()
    password = message.text or user_data.get("generated_password")
    await state.update_data(password=password)

    # Проверяем роль создателя
    user_role = await api_client.get_user_role(message.from_user.id)
    if user_role == "super_admin":
        # Показываем кнопки выбора роли
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="super_admin"), KeyboardButton(text="admin")],
                [KeyboardButton(text="worker"), KeyboardButton(text="user")]
            ],
            resize_keyboard=True,
        )
        await message.answer("Выберите роль нового пользователя:", reply_markup=keyboard)
        await state.set_state(CreateUserStates.waiting_role)
    else:
        # Если не super_admin — роль по умолчанию 'user'
        await state.update_data(role="user")
        await create_user_finalize(message, state, api_client)

@start_router.message(IsGroupWithOwner, CreateUserStates.waiting_role)
async def create_user_role(message: Message, state: FSMContext, api_client: DjangoAPIClient):
    role = message.text if message.text in ["super_admin", "admin", "worker", "user"] else "user"
    await state.update_data(role=role)
    await create_user_finalize(message, state, api_client)

