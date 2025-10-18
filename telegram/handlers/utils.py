from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import secrets
import string
from models import EmailAccount, SessionLocal

def make_user_buttons(users_page):
    buttons = [
        [InlineKeyboardButton(text=f"{u['username']} {'✅' if u['last_login'] else ''}", callback_data=f"user_{u['id']}")]
        for u in users_page["results"]
    ]

    # Навигация
    nav_buttons = []
    if users_page["previous"]:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"users_page_{users_page['previous'].split('=')[-1]}"))
    if users_page["next"]:
        nav_buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"users_page_{users_page['next'].split('=')[-1]}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def add_email(email, password):
    db = SessionLocal()
    if db.query(EmailAccount).filter_by(email=email).first():
        return "❌ Такая почта уже есть"
    new_email = EmailAccount(email=email, password=password)
    db.add(new_email)
    db.commit()
    return "✅ Почта добавлена"

def delete_email(email):
    db = SessionLocal()
    acc = db.query(EmailAccount).filter_by(email=email).first()
    if not acc:
        return "❌ Почта не найдена"
    db.delete(acc)
    db.commit()
    return "✅ Почта удалена"

def list_emails():
    db = SessionLocal()
    accounts = db.query(EmailAccount).all()
    return [a.email for a in accounts]