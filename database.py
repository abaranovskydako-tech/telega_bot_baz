# database.py
import os
import logging
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

logger = logging.getLogger(__name__)

# Оптимизированная конфигурация для Render
def get_database_path():
    """Получаем оптимальный путь для базы данных на Render"""
    # Приоритет переменной окружения
    env_path = os.environ.get("DATABASE_PATH")
    if env_path:
        return env_path
    
    # На Render используем /tmp для временных файлов или текущую директорию
    if os.environ.get("RENDER"):
        # На Render используем текущую рабочую директорию
        db_path = Path.cwd() / "questionnaire.db"
        logger.info(f"Using Render environment, database path: {db_path}")
        return str(db_path)
    else:
        # Локальная разработка
        db_path = Path.cwd() / "questionnaire.db"
        logger.info(f"Using local environment, database path: {db_path}")
        return str(db_path)

# Создаем движок базы данных с оптимизациями для Render
DB_PATH = get_database_path()

# Проверяем доступность директории для записи
try:
    db_dir = Path(DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Database directory ensured: {db_dir}")
except Exception as e:
    logger.error(f"Cannot create database directory {db_dir}: {e}")
    # Fallback на временную директорию
    DB_PATH = str(Path(tempfile.gettempdir()) / "questionnaire.db")
    logger.info(f"Using fallback database path: {DB_PATH}")

# Создаем движок с оптимизациями для SQLite
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,  # Отключаем SQL логи для продакшена
    connect_args={
        "check_same_thread": False,  # Разрешаем многопоточность
        "timeout": 30,  # Таймаут подключения
    },
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,  # Пересоздание соединений каждый час
)

# Создаем базовый класс для моделей
Base = declarative_base()

# Модель для ответов опроса
class SurveyResponse(Base):
    __tablename__ = 'survey_responses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)  # Добавляем индекс для быстрого поиска
    full_name = Column(String(255), nullable=False)  # Ограничиваем длину строки
    birth_date = Column(Date, nullable=False)
    citizenship = Column(String(100), nullable=False)  # Ограничиваем длину строки
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Добавляем индекс для сортировки
    
    def __repr__(self):
        return f"<SurveyResponse(user_id={self.user_id}, full_name='{self.full_name}', citizenship='{self.citizenship}')>"

# Создаем сессию для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создаём таблицу для ответов, если её ещё нет"""
    global engine, DB_PATH, SessionLocal
    
    try:
        # Проверяем доступность файла базы данных
        db_file = Path(DB_PATH)
        if db_file.exists():
            logger.info(f"Database file exists: {db_file} (size: {db_file.stat().st_size} bytes)")
        else:
            logger.info(f"Creating new database file: {db_file}")
        
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        
        # Проверяем, что таблица создалась
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='survey_responses'"))
            if result.fetchone():
                logger.info(f"Database initialized successfully at {DB_PATH}")
                return True
            else:
                logger.error("Table creation failed - table not found after creation")
                return False
                
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # Попытка создать базу в временной директории
        try:
            fallback_path = str(Path(tempfile.gettempdir()) / "questionnaire_fallback.db")
            logger.info(f"Trying fallback database path: {fallback_path}")
            
            DB_PATH = fallback_path
            engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base.metadata.create_all(bind=engine)
            logger.info(f"Fallback database created successfully at {fallback_path}")
            return True
        except Exception as fallback_error:
            logger.error(f"Fallback database creation also failed: {fallback_error}")
            return False

def get_database_info():
    """Получаем информацию о базе данных"""
    try:
        db_file = Path(DB_PATH)
        if db_file.exists():
            size = db_file.stat().st_size
            modified = datetime.fromtimestamp(db_file.stat().st_mtime)
            return {
                "path": str(db_file),
                "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 2),
                "last_modified": modified,
                "exists": True
            }
        else:
            return {"exists": False, "path": str(db_file)}
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"error": str(e)}

def save_response(user_id: int, full_name: str, birth_date: str, citizenship: str):
    """Сохраняем один ответ опроса"""
    session = None
    try:
        # Создаем сессию
        session = SessionLocal()
        
        # Конвертируем дату из строки в объект Date
        if birth_date:
            try:
                # Если дата уже в формате YYYY-MM-DD
                if '-' in birth_date:
                    parsed_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                else:
                    # Если дата в формате ДД.ММ.ГГГГ
                    parsed_date = datetime.strptime(birth_date, '%d.%m.%Y').date()
            except ValueError:
                logger.error(f"Invalid date format: {birth_date}")
                parsed_date = None
        else:
            parsed_date = None
        
        # Создаем новый ответ
        new_response = SurveyResponse(
            user_id=user_id,
            full_name=full_name,
            birth_date=parsed_date,
            citizenship=citizenship
        )
        
        # Добавляем в сессию и сохраняем
        session.add(new_response)
        session.commit()
        
        # Получаем ID нового ответа
        new_id = new_response.id
        
        logger.info(f"Survey response saved successfully with ID {new_id}")
        
        # Логируем информацию о базе данных после сохранения
        db_info = get_database_info()
        if db_info.get("exists"):
            logger.info(f"Database size after save: {db_info['size_mb']} MB")
        
        return new_id
        
    except Exception as e:
        logger.error(f"Error saving survey response: {e}")
        if session:
            session.rollback()
        return None
    finally:
        if session:
            session.close()

def get_user_responses(user_id: int):
    """Получаем все ответы пользователя"""
    session = None
    try:
        session = SessionLocal()
        responses = session.query(SurveyResponse).filter(SurveyResponse.user_id == user_id).all()
        logger.info(f"Retrieved {len(responses)} responses for user {user_id}")
        return responses
    except Exception as e:
        logger.error(f"Error getting user responses: {e}")
        return []
    finally:
        if session:
            session.close()

def get_all_responses():
    """Получаем все ответы (для администратора)"""
    session = None
    try:
        session = SessionLocal()
        responses = session.query(SurveyResponse).all()
        logger.info(f"Retrieved {len(responses)} total responses")
        return responses
    except Exception as e:
        logger.error(f"Error getting all responses: {e}")
        return []
    finally:
        if session:
            session.close()

def health_check():
    """Проверка здоровья базы данных"""
    try:
        # Проверяем подключение
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        # Проверяем информацию о базе
        db_info = get_database_info()
        
        return {
            "status": "healthy",
            "database": db_info,
            "connection": "ok"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection": "failed"
        }
