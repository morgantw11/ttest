import smtplib
from email.mime.text import MIMEText
from jinja2 import Template
from models import EmailAccount, SessionLocal
import random


def send_email(receiver_email,login,password,magic_link,big_text):

    with open("email_sender.html") as file:
        template_content = file.read()
    
    template = Template(template_content)
    db = SessionLocal()
    account = db.query(EmailAccount).all()
    db.close()

    if not account:
        return "❌ Нет доступных почтовых аккаунтов"
    

    
    html_content = template.render(
            login=login,
            password=password,
            magic_link=magic_link,
            big_text=big_text
        )
    
    for attempt in range(3):
        sender_account = random.choice(account)
        sender_db = sender_account.email
        password_db = sender_account.password

        try:
            # Подключаемся через SSL
            server = smtplib.SMTP_SSL("smtp.hostinger.com", 465)
            server.login(sender_db, password_db)

            # Формируем письмо с заголовками
            msg = MIMEText(html_content,"html")
            msg["From"] = sender_db # сюда вставить 
            msg["To"] = receiver_email
            msg["Subject"] = f"Welcome to Tommorow! {big_text} invites you to sign acontract!"

            server.sendmail(sender_db, receiver_email, msg.as_string())
            server.quit()

            return "✅ Почта была успешно отправлена!"

        except Exception as _ex:
            accounts = [acc for acc in accounts if acc.email != sender_db]
            
            if not accounts:  # если почт больше нет
                return f"❌ Ошибка: все аккаунты недоступны.\nПоследняя ошибка: {_ex}"
            
        
    return "❌ Не удалось отправить письмо после 3 попыток."



