from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import secrets
import string
from models import EmailAccount, SessionLocal

def make_user_buttons(users_page):
    try:
        print("🔍 DEBUG: make_user_buttons started")
        
        buttons = [
            [InlineKeyboardButton(
                text=f"{u['username']} {'✅' if u['last_login'] else ''}", 
                callback_data=f"user_{u['id']}"
            )]
            for u in users_page["results"]
        ]
        print("🔍 DEBUG: User buttons created")

        # Навигация - правильный разбор номеров страниц
        nav_buttons = []
        
        # ВСЕГДА показываем "Назад" если есть предыдущая страница
        if users_page.get("previous"):
            print(f"🔍 DEBUG: previous exists: {users_page['previous']}")
            prev_page = extract_page_number(users_page["previous"])
            print(f"🔍 DEBUG: prev_page extracted: {prev_page}")
            if prev_page:
                print("🔍 DEBUG: Creating 'Back' button")
                nav_buttons.append(InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data=f"users_page_{prev_page}"
                ))
                print("🔍 DEBUG: 'Back' button added")
        
        # ВСЕГДА показываем "Вперед" если есть следующая страница
        if users_page.get("next"):
            print(f"🔍 DEBUG: next exists: {users_page['next']}")
            next_page = extract_page_number(users_page["next"])
            print(f"🔍 DEBUG: next_page extracted: {next_page}")
            if next_page:
                print("🔍 DEBUG: Creating 'Forward' button")
                nav_buttons.append(InlineKeyboardButton(
                    text="➡️ Вперед", 
                    callback_data=f"users_page_{next_page}"
                ))
                print("🔍 DEBUG: 'Forward' button added")
        
        print(f"🔍 DEBUG: nav_buttons count: {len(nav_buttons)}")
        
        if nav_buttons:
            buttons.append(nav_buttons)

        print("🔍 DEBUG: Returning keyboard")
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    except Exception as e:
        print(f"❌ Error in make_user_buttons: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Ошибка отображения", callback_data="error")]]
        )

def extract_page_number(url):
    """Безопасно извлекает номер страницы из URL"""
    if not url:
        return None
    
    try:
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        page = query_params.get('page', [None])[0]
        return page
    except:
        return None


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