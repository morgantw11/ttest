from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove
from filters import IsGroupWithOwner
from api_client import  DjangoAPIClient
from .start_handlers import start_router



@start_router.message(IsGroupWithOwner, F.text == "⚠️ Карантин")
async def carantin_message(message: Message, api_client : DjangoAPIClient):
        checker = await api_client.get_system_states(message.from_user.id)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Выключить' if checker['carantin'] else 'Включить'}\n", callback_data="disable_carantin" if checker["carantin"] else "enable_carantin")],
            ]
        
        )
        await message.answer(f"😷 Карантин: {'🟢 ВКЛ' if checker['carantin'] else '🔴 ВЫКЛ'}\n",reply_markup=keyboard)


@start_router.callback_query(IsGroupWithOwner,F.data.startswith("disable_carantin"))
async def disable_carantin_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
        data, status = await api_client.get(callback.from_user.id, f"api/mode/carantin/delete")
        if status == 200:
            checker = await api_client.get_system_states(callback.from_user.id)
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Выключить' if checker['carantin'] else 'Включить'}\n", callback_data="disable_carantin" if checker["carantin"] else "enable_carantin")],
            ]
        
            )
            await callback.message.edit_text(f"😷 Карантин: {'🟢 ВКЛ' if checker['carantin'] else '🔴 ВЫКЛ'}\n",reply_markup=keyboard)
            #await carantin_message(callback.message, api_client)

@start_router.callback_query(IsGroupWithOwner,F.data.startswith("enable_carantin"))
async def enable_carantin_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
        data, status = await api_client.get(callback.from_user.id, f"api/mode/carantin/create")
        if status == 200:
            checker = await api_client.get_system_states(callback.from_user.id)
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Выключить' if checker['carantin'] else 'Включить'}\n", callback_data="disable_carantin" if checker["carantin"] else "enable_carantin")],
            ]
        
            )
            await callback.message.edit_text(f"😷 Карантин: {'🟢 ВКЛ' if checker['carantin'] else '🔴 ВЫКЛ'}\n",reply_markup=keyboard)
            


@start_router.message(IsGroupWithOwner, F.text == "✅ Вайтлист")
async def whitlist_message(message: Message, api_client : DjangoAPIClient):
    user_role = await api_client.get_user_role(message.from_user.id)
    if user_role == 'super_admin' or user_role == 'admin':
        checker = await api_client.get_system_states(message.from_user.id)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Включить' if checker['whitelist'] else 'Выключить'}\n", callback_data="enable_whitelist" if checker["carantin"] else "disable_whitelist")],
            ]
        
        )
        await message.answer(f"📄 Вайтлист: {'🔴 ВЫКЛ' if checker['whitelist'] else '🟢 ВКЛ'}\n",reply_markup=keyboard)
    else:
        await message.answer("❌ Доступ запрещен", show_alert=True)


@start_router.callback_query(IsGroupWithOwner,F.data.startswith("disable_whitelist"))
async def disable_whitlist_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(callback.from_user.id)
    if user_role == 'super_admin' or user_role == 'admin':
        data, status = await api_client.get(callback.from_user.id, f"api/mode/white-list/create")
        if status == 200:
            checker = await api_client.get_system_states(callback.from_user.id)
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Включить' if checker['whitelist'] else 'Выключить'}\n", callback_data="enable_whitelist" if checker["whitelist"] else "disable_whitelist")],
            ]
        
            )
            await callback.message.edit_text(f"📄 Вайтлист: {'🔴 ВЫКЛ' if checker['whitelist'] else '🟢 ВКЛ'}\n",reply_markup=keyboard)
            #await carantin_message(callback.message, api_client)

    else:
        await callback.answer("❌ Доступ запрещен", show_alert=True)

@start_router.callback_query(IsGroupWithOwner,F.data.startswith("enable_whitelist"))
async def enable_whitlist_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(callback.from_user.id)
    if user_role == 'super_admin' or user_role == 'admin':
        data, status = await api_client.get(callback.from_user.id, f"api/mode/white-list/delete")
        if status == 200:
            checker = await api_client.get_system_states(callback.from_user.id)
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Включить' if checker['whitelist'] else 'Выключить'}\n", callback_data="enable_whitelist" if checker["carantin"] else "disable_whitelist")],
            ]
        
            )
            await callback.message.edit_text(f"📄 Вайтлист: {'🔴 ВЫКЛ' if checker['whitelist'] else '🟢 ВКЛ'}\n",reply_markup=keyboard)
            

    else:
        await callback.answer("❌ Доступ запрещен", show_alert=True)



@start_router.message(IsGroupWithOwner, F.text == "💀 Ошибка 503")
async def error_503_message(message: Message, api_client : DjangoAPIClient):
    user_role = await api_client.get_user_role(message.from_user.id)
    if user_role == 'super_admin' or user_role == 'admin':
        checker = await api_client.get_system_states(message.from_user.id)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Выключить' if checker['error_503'] else 'Включить'}\n", callback_data="disable_503" if checker["error_503"] else "enable_503")],
            ]
        
        )
        await message.answer(f"💀Ошибка 503: {'🟢 ВКЛ' if checker['error_503'] else '🔴 ВЫКЛ'}\n",reply_markup=keyboard)
    else:
        await message.answer("❌ Доступ запрещен", show_alert=True)


@start_router.callback_query(IsGroupWithOwner,F.data.startswith("disable_503"))
async def disable_carantin_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(callback.from_user.id)
    if user_role == 'super_admin' or user_role == 'admin':
        data, status = await api_client.get(callback.from_user.id, f"api/mode/503/delete")
        if status == 200:
            checker = await api_client.get_system_states(callback.from_user.id)
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Выключить' if checker['error_503'] else 'Включить'}\n", callback_data="disable_503" if checker["error_503"] else "enable_503")],
            ]
        
            )
            await callback.message.edit_text(f"💀Ошибка 503: {'🟢 ВКЛ' if checker['error_503'] else '🔴 ВЫКЛ'}\n",reply_markup=keyboard)
            #await carantin_message(callback.message, api_client)

    else:
        await callback.answer("❌ Доступ запрещен", show_alert=True)

@start_router.callback_query(IsGroupWithOwner,F.data.startswith("enable_503"))
async def enable_carantin_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(callback.from_user.id)
    if user_role == 'super_admin' or user_role == 'admin':
        data, status = await api_client.get(callback.from_user.id, f"api/mode/503/create")
        if status == 200:
            checker = await api_client.get_system_states(callback.from_user.id)
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Выключить' if checker['error_503'] else 'Включить'}\n", callback_data="disable_503" if checker["error_503"] else "enable_503")],
            ]
        
            )
            await callback.message.edit_text(f"💀Ошибка 503: {'🟢 ВКЛ' if checker['error_503'] else '🔴 ВЫКЛ'}\n",reply_markup=keyboard)
            

    else:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
