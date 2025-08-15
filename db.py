# db.py
import os
import sys
import re
import ssl
from sqlalchemy import create_engine, text, Integer, Text, Column, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, urlsplit, urlunsplit, parse_qsl, urlencode

# 1) Берём адрес базы из переменной окружения (environment variable)
DATABASE_URL = os.getenv("DATABASE_URL")

def _normalize(url: str) -> str:
    if not url:
        return url
    # 1) Драйвер pg8000
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+pg8000://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+pg8000://", 1)

    # 2) SSL для pg8000 - убираем параметры из URL, SSL будет в connect_args
    if "+pg8000://" in url:
        parts = urlsplit(url)
        q = dict(parse_qsl(parts.query, keep_blank_values=True))
        # Удаляем SSL параметры, так как SSL будет настроен через connect_args
        q.pop("ssl", None)
        q.pop("sslmode", None)
        url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))
    return url

# 2) Выбираем: облако (PostgreSQL) или локально (SQLite)
if DATABASE_URL:
    db_url = _normalize(DATABASE_URL)
else:
    db_url = "sqlite:///telega.db"

# Отладочная печать без пароля
_drv = "pg8000" if "+pg8000" in db_url else ("psycopg" if "+psycopg" in db_url else "default")
_ver = sys.version.split()[0]
_safe = re.sub(r"://[^:@]+:([^@]+)@", "://***:***@", db_url)

# Формируем connect_args в зависимости от драйвера
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif "+pg8000" in db_url:
    connect_args = {"ssl_context": ssl.create_default_context()}

print(f"[db] driver={'pg8000' if '+pg8000' in db_url else 'other'} connect_args={list(connect_args.keys())}")

# 3) Движок и сессии
engine = create_engine(
    db_url,
    pool_pre_ping=True,
    connect_args=connect_args
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# 4) Модель таблицы
class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    question = Column(Text)
    answer = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

# Модель для survey_responses
class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    full_name = Column(Text, nullable=False)
    birth_date = Column(Text, nullable=False)  # Храним как текст для совместимости
    citizenship = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

# 5) Инициализация схемы
def init_db():
    Base.metadata.create_all(bind=engine)

# 6) Утилита сохранения
def save_response(user_id: int, question: str, answer: str):
    with SessionLocal() as s:
        s.add(Response(user_id=user_id, question=question, answer=answer))
        s.commit()

# Утилита сохранения для survey_responses
def save_survey_response(user_id: int, full_name: str, birth_date: str, citizenship: str):
    with SessionLocal() as s:
        new_response = SurveyResponse(
            user_id=user_id,
            full_name=full_name,
            birth_date=birth_date,
            citizenship=citizenship
        )
        s.add(new_response)
        s.commit()
        return new_response.id
