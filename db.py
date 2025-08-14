# db.py
import os
import sys
import re
from sqlalchemy import create_engine, text, Integer, Text, Column, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse

# 1) Берём адрес базы из переменной окружения (environment variable)
DATABASE_URL = os.getenv("DATABASE_URL")

def _normalize(url: str) -> str:
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

# 2) Выбираем: облако (PostgreSQL) или локально (SQLite)
if DATABASE_URL:
    db_url = _normalize(DATABASE_URL)
else:
    db_url = "sqlite:///telega.db"

# Отладочная печать без пароля
_drv = "psycopg" if "+psycopg" in db_url else "default"
_ver = sys.version.split()[0]
_safe = re.sub(r"://[^:@]+:([^@]+)@", "://***:***@", db_url)
print(f"[db] python={_ver} driver={_drv} url={_safe}")

# 3) Движок и сессии
engine = create_engine(
    db_url,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {}
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

# 5) Инициализация схемы
def init_db():
    Base.metadata.create_all(bind=engine)

# 6) Утилита сохранения
def save_response(user_id: int, question: str, answer: str):
    with SessionLocal() as s:
        s.add(Response(user_id=user_id, question=question, answer=answer))
        s.commit()
