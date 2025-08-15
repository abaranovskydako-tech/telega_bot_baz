#!/usr/bin/env python3
"""
Скрипт для исправления типов данных в PostgreSQL таблице
"""

import os
import logging
from sqlalchemy import create_engine, text
import ssl

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_postgres_types():
    """Исправляет типы данных в PostgreSQL таблице"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL не установлен")
        return False
    
    # Нормализуем URL для pg8000
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif database_url.startswith("postgresql://") and "+pg8000" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)
    
    # Убираем sslmode из URL
    if "?sslmode=" in database_url:
        database_url = database_url.split("?")[0]
    
    logger.info(f"Подключение к PostgreSQL: {database_url.replace('://', '://***:***@')}")
    
    # Создаем engine с SSL контекстом
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    engine = create_engine(
        database_url, 
        pool_pre_ping=True, 
        connect_args={"ssl_context": ssl_context}
    )
    
    try:
        with engine.connect() as conn:
            # Проверяем текущую структуру
            logger.info("Текущая структура таблицы:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'survey_responses'
                ORDER BY ordinal_position;
            """))
            
            for row in result:
                logger.info(f"  {row.column_name}: {row.data_type}")
            
            # Изменяем тип user_id на BIGINT
            logger.info("Изменяю тип user_id на BIGINT...")
            conn.execute(text("ALTER TABLE survey_responses ALTER COLUMN user_id TYPE BIGINT"))
            conn.commit()
            
            # Проверяем результат
            logger.info("Новая структура таблицы:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'survey_responses'
                ORDER BY ordinal_position;
            """))
            
            for row in result:
                logger.info(f"  {row.column_name}: {row.data_type}")
            
            logger.info("Типы данных исправлены успешно!")
            return True
            
    except Exception as e:
        logger.error(f"Ошибка исправления типов: {e}")
        return False

if __name__ == "__main__":
    fix_postgres_types()
