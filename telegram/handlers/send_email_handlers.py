from .start_handlers import start_router
from filters import IsGroupWithOwner
from aiogram import Router, F,Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram3_di import Depends
from api_client import  SessionExpiredError,DjangoAPIClient
from datetime import datetime
from .utils import list_emails,delete_email,add_email

class AddEmailState(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()

@start_router.message(IsGroupWithOwner, F.text == "✉️ Почта")
async def email_message(message: Message, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(message.from_user.id)
    if user_role != 'super_admin':
        await message.answer("❌ Доступ запрещен", show_alert=True)
        return

    emails = list_emails()
    keyboardmenu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💌 Добавить почту")],
            [KeyboardButton(text="🏠 Выйти в главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню'
    )

    if emails:
        text = "📧 Список почт:"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=email, callback_data=f"deleteemail:{email}")]
                for email in emails
            ]
        )
    else:
        text = "⚠️ Пока нет добавленных почт."
        keyboard = None
    await message.answer("Нажмите на почту, чтобы её удалить.", reply_markup=keyboardmenu)
    await message.answer(text, reply_markup=keyboard)

@start_router.callback_query(F.data.startswith("deleteemail:"))
async def delete_email_callback(callback: CallbackQuery):
    email = callback.data.split(":", 1)[1]  # вытаскиваем email из callback_data
    result = delete_email(email)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✉️ Почта")],
            [KeyboardButton(text="🏠 Выйти в главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню'
    )
    await callback.message.answer(f"{result}\n\n📧 Обновите список, чтобы увидеть актуальные данные.",reply_markup=keyboard)


@start_router.message(IsGroupWithOwner, F.text == "💌 Добавить почту")
async def add_email_start(message: Message, state: FSMContext, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(message.from_user.id)
    if user_role != 'super_admin':
        await message.answer("❌ Доступ запрещен", show_alert=True)
        return
    await message.answer("📧 Введите email для добавления:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddEmailState.waiting_for_email)


@start_router.message(AddEmailState.waiting_for_email)
async def add_email_get_email(message: Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(email=email)
    await message.answer("🔑 Теперь введите пароль от этой почты:")
    await state.set_state(AddEmailState.waiting_for_password)


@start_router.message(AddEmailState.waiting_for_password)
async def add_email_get_password(message: Message, state: FSMContext):
    data = await state.get_data()
    email = data["email"]
    password = message.text.strip()

    result = add_email(email, password)  # твоя функция работы с БД

    await message.answer(result, reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✉️ Почта")],
            [KeyboardButton(text="🏠 Выйти в главное меню")]
        ],
        resize_keyboard=True
    ))
    await state.clear()