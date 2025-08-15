#!/usr/bin/env python3
"""
Скрипт миграции данных из SQLite в PostgreSQL
Использует SQLAlchemy для безопасной миграции с защитой от дублей
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mask_password(url):
    """Маскирует пароль в URL для безопасного логирования"""
    if not url:
        return url
    parts = url.split('@')
    if len(parts) == 2:
        auth_part = parts[0].split('://')[1]
        if ':' in auth_part:
            username, password = auth_part.split(':', 1)
            masked_url = url.replace(f":{password}@", ":***@")
            return masked_url
    return url

def find_sqlite_file(sqlite_path=None):
    """Находит SQLite файл для миграции"""
    if sqlite_path and os.path.exists(sqlite_path):
        return sqlite_path
    
    # Ищем автоматически
    possible_files = ['telega.db', 'questionnaire.db']
    for file in possible_files:
        if os.path.exists(file):
            logger.info(f"Найден SQLite файл: {file}")
            return file
    
    logger.error("SQLite файл не найден. Укажите путь через --sqlite PATH")
    return None

def create_sqlite_engine(sqlite_path):
    """Создает engine для SQLite"""
    sqlite_url = f"sqlite:///{sqlite_path}"
    logger.info(f"Подключение к SQLite: {sqlite_path}")
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_postgres_engine():
    """Создает engine для PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL не установлен. Установите переменную окружения для подключения к PostgreSQL")
    
    # Нормализуем URL для pg8000 и убираем sslmode из URL
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif database_url.startswith("postgresql://") and "+pg8000" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)
    
    # Убираем sslmode из URL, так как pg8000 не поддерживает этот параметр
    if "?sslmode=" in database_url:
        base_url = database_url.split("?")[0]
        database_url = base_url
    
    masked_url = mask_password(database_url)
    logger.info(f"Подключение к PostgreSQL: {masked_url}")
    
    # Создаем engine с SSL контекстом для pg8000
    connect_args = {}
    if "+pg8000" in database_url:
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args = {"ssl_context": ssl_context}
    
    return create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)

def count_records(engine, table_name="survey_responses"):
    """Подсчитывает количество записей в таблице"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            return count
    except Exception as e:
        logger.error(f"Ошибка подсчета записей в {table_name}: {e}")
        return 0

def migrate_data_simple(sqlite_engine, postgres_engine, batch_size=1000, dry_run=False):
    """Упрощенная миграция данных из SQLite в PostgreSQL"""
    
    # Подсчитываем записи в SQLite
    sqlite_count = count_records(sqlite_engine, "survey_responses")
    logger.info(f"Записей в SQLite: {sqlite_count}")
    
    if sqlite_count == 0:
        logger.info("В SQLite нет данных для миграции")
        return sqlite_count, 0, 0
    
    if dry_run:
        logger.info("DRY RUN: данные не будут изменены")
        return sqlite_count, 0, 0
    
    # Подсчитываем записи в PostgreSQL до миграции
    postgres_count_before = count_records(postgres_engine, "survey_responses")
    logger.info(f"Записей в PostgreSQL до миграции: {postgres_count_before}")
    
    inserted_count = 0
    skipped_count = 0
    
    try:
        with sqlite_engine.connect() as sqlite_conn, postgres_engine.connect() as postgres_conn:
            # Читаем данные из SQLite пакетами
            offset = 0
            while offset < sqlite_count:
                # Читаем пакет данных
                query = text(f"SELECT id, user_id, full_name, birth_date, citizenship, created_at FROM survey_responses ORDER BY id LIMIT {batch_size} OFFSET {offset}")
                result = sqlite_conn.execute(query)
                rows = result.fetchall()
                
                if not rows:
                    break
                
                logger.info(f"Обрабатываю пакет {offset//batch_size + 1}: {len(rows)} записей")
                
                # Вставляем в PostgreSQL с защитой от дублей
                for row in rows:
                    try:
                        # Используем простой INSERT с проверкой существования
                        check_query = text("SELECT id FROM survey_responses WHERE id = :id")
                        exists = postgres_conn.execute(check_query, {"id": row.id}).fetchone()
                        
                        if exists:
                            skipped_count += 1
                            continue
                        
                        # Вставляем новую запись
                        insert_query = text("""
                            INSERT INTO survey_responses (id, user_id, full_name, birth_date, citizenship, created_at)
                            VALUES (:id, :user_id, :full_name, :birth_date, :citizenship, :created_at)
                        """)
                        
                        postgres_conn.execute(insert_query, {
                            "id": row.id,
                            "user_id": row.user_id,
                            "full_name": row.full_name,
                            "birth_date": row.birth_date,
                            "citizenship": row.citizenship,
                            "created_at": row.created_at
                        })
                        
                        inserted_count += 1
                            
                    except Exception as e:
                        logger.warning(f"Ошибка вставки записи {row.id}: {e}")
                        skipped_count += 1
                        # Откатываем транзакцию при ошибке
                        postgres_conn.rollback()
                        # Создаем новую транзакцию
                        postgres_conn.begin()
                
                # Коммитим пакет
                try:
                    postgres_conn.commit()
                except Exception as e:
                    logger.warning(f"Ошибка коммита пакета: {e}")
                    postgres_conn.rollback()
                    # Создаем новую транзакцию
                    postgres_conn.begin()
                
                offset += batch_size
                
        # Выравниваем sequence
        try:
            with postgres_engine.connect() as conn:
                conn.execute(text("SELECT setval('survey_responses_id_seq', (SELECT COALESCE(MAX(id), 1) FROM survey_responses))"))
                conn.commit()
                logger.info("Sequence выровнен")
        except Exception as e:
            logger.warning(f"Ошибка выравнивания sequence: {e}")
        
    except Exception as e:
        logger.error(f"Ошибка миграции: {e}")
        raise
    
    return sqlite_count, inserted_count, skipped_count

def main():
    parser = argparse.ArgumentParser(description="Миграция данных из SQLite в PostgreSQL")
    parser.add_argument("--sqlite", help="Путь к SQLite файлу")
    parser.add_argument("--dry-run", action="store_true", help="Только проверка без изменения данных")
    parser.add_argument("--batch-size", type=int, default=1000, help="Размер пакета для миграции")
    
    args = parser.parse_args()
    logger.info(f"Аргументы: sqlite={args.sqlite}, dry_run={args.dry_run}, batch_size={args.batch_size}")
    
    try:
        # Находим SQLite файл
        sqlite_path = find_sqlite_file(args.sqlite)
        if not sqlite_path:
            sys.exit(1)
        
        # Создаем engines
        sqlite_engine = create_sqlite_engine(sqlite_path)
        postgres_engine = create_postgres_engine()
        
        # Выполняем миграцию
        sqlite_count, inserted_count, skipped_count = migrate_data_simple(
            sqlite_engine, postgres_engine, args.batch_size, args.dry_run
        )
        
        # Выводим результаты
        logger.info("=" * 50)
        logger.info("РЕЗУЛЬТАТЫ МИГРАЦИИ:")
        logger.info(f"Записей в SQLite: {sqlite_count}")
        logger.info(f"Вставлено в PostgreSQL: {inserted_count}")
        logger.info(f"Пропущено как дубликаты: {skipped_count}")
        
        if not args.dry_run:
            postgres_count_after = count_records(postgres_engine, "survey_responses")
            logger.info(f"Итоговое количество в PostgreSQL: {postgres_count_after}")
            
            # Примеры запросов для валидации
            logger.info("=" * 50)
            logger.info("ЗАПРОСЫ ДЛЯ ВАЛИДАЦИИ:")
            logger.info("SELECT COUNT(*) FROM public.survey_responses;")
            logger.info("SELECT * FROM public.survey_responses ORDER BY id DESC LIMIT 20;")
        
        logger.info("=" * 50)
        logger.info("Миграция завершена успешно!")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
