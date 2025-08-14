import os
from db import init_db, save_response

def init_survey_database():
    """Инициализация базы данных для опроса персональных данных."""
    
    # Инициализируем новую базу данных через db.py
    init_db()
    print("✅ База данных инициализирована через db.py")
    
    # Добавляем тестовые данные
    test_user_id = 12345
    save_response(test_user_id, "Тест", "Тестовые данные")
    
    print("📋 База данных готова к использованию")
    print("🎯 Готов к сбору персональных данных через db.py")

if __name__ == "__main__":
    init_survey_database()
