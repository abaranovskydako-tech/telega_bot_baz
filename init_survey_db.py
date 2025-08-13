import sqlite3
import os

def init_survey_database():
    """Инициализация базы данных для опроса персональных данных."""
    
    # Создаем базу данных
    db_path = './questionnaire.db'
    
    # Удаляем старую базу если существует
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Удалена старая база данных: {db_path}")
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем таблицу опросов
    cursor.execute('''
        CREATE TABLE surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            survey_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Создаем таблицу персональных данных
    cursor.execute('''
        CREATE TABLE personal_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER,
            full_name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            citizenship TEXT NOT NULL,
            phone_number TEXT,
            email TEXT,
            address TEXT,
            passport_number TEXT,
            passport_series TEXT,
            passport_issued_by TEXT,
            passport_issue_date TEXT,
            inn TEXT,
            snils TEXT,
            education TEXT,
            occupation TEXT,
            income_level TEXT,
            marital_status TEXT,
            children_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (survey_id) REFERENCES surveys (id)
        )
    ''')
    
    # Добавляем тестовые данные
    cursor.execute('''
        INSERT INTO questionnaires (title, description) 
        VALUES ('Опрос персональных данных', 'Сбор персональных данных пользователей')
    ''')
    
    # Сохраняем изменения
    conn.commit()
    conn.close()
    
    print(f"✅ База данных создана: {db_path}")
    print("📋 Созданы таблицы: users, surveys, personal_data")
    print("🎯 Готов к сбору персональных данных")

if __name__ == "__main__":
    init_survey_database()
