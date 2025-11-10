from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import secrets
import string
from models import EmailAccount, SessionLocal

def make_user_buttons(users_page):
    try:
        buttons = [
            [InlineKeyboardButton(
                text=f"{u['username']} {'✅' if u['last_login'] else ''}", 
                callback_data=f"user_{u['id']}"
            )]
            for u in users_page["results"]
        ]

        # Навигация - правильный разбор номеров страниц
        nav_buttons = []
                # ВСЕГДА показываем "Назад" если есть предыдущая страница
        if users_page.get("previous"):
            prev_page = extract_page_number(users_page["previous"])
            if prev_page:
                nav_buttons.append(InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data=f"users_page_{prev_page}"
                ))

                
        # ВСЕГДА показываем "Вперед" если есть следующая страница
        if users_page.get("next"):
            next_page = extract_page_number(users_page["next"])
            if next_page:
                nav_buttons.append(InlineKeyboardButton(
                    text="➡️ Вперед", 
                    callback_data=f"users_page_{next_page}"
                ))
        
        # Добавляем навигационные кнопки только если они есть
        if nav_buttons:
            buttons.append(nav_buttons)

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    except Exception as e:
        print(f"Error in make_user_buttons: {e}")
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Ошибка отображения", callback_data="error")]]
        )

def extract_page_number(url):
    """Безопасно извлекает номер страницы из URL для любого endpoint"""
    if not url:
        return None
    
    try:
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        page = query_params.get('page', [None])[0]
        
        if page:
            return page
        
        # Список всех endpoints которые поддерживают пагинацию
        paginated_endpoints = [
            '/api/users',
            '/api/users/',
            '/api/users/created-by-me',
            '/api/users/created-by-me/',
            '/api/workers', 
            '/api/workers/',
            # добавьте другие endpoints по мере необходимости
        ]
        
        clean_path = parsed_url.path.rstrip('/')
        if clean_path in [ep.rstrip('/') for ep in paginated_endpoints]:
            return "1"
            
        return None
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