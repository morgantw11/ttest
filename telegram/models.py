from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Telegram user_id
    sessionid = Column(String(255), nullable=False)
    csrftoken = Column(String(255))
    django_user_id = Column(Integer)  # Опционально: ID пользователя в Django


class EmailAccount(Base):
    __tablename__ = 'email_accounts'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    
engine = create_engine('sqlite:///sessions.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


