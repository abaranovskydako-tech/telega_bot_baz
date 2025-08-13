#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к базе данных и функциональности.
Запустите это для проверки подключения к базе данных перед запуском бота.
"""

import os
from dotenv import load_dotenv
from database import DatabaseManager

def test_database_connection():
    """Тестирование подключения к базе данных и базовых операций."""
    print("🔍 Тестирование подключения к базе данных...")
    
    # Загрузка переменных окружения
    load_dotenv()
    
    # Получение конфигурации
    db_path = os.getenv('DATABASE_PATH', 'remote_database.db')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    
    print(f"📁 Путь к базе данных: {db_path}")
    print(f"👤 Имя пользователя: {username or 'Не установлено'}")
    print(f"🔑 Пароль: {'Установлен' if password else 'Не установлен'}")
    print()
    
    # Инициализация менеджера базы данных
    db_manager = DatabaseManager(db_path, username, password)
    
    # Тестирование подключения
    print("🔌 Попытка подключения...")
    if db_manager.connect():
        print("✅ Подключение к базе данных успешно!")
        
        # Тестирование получения таблиц
        print("\n📊 Получение списка таблиц...")
        tables = db_manager.get_all_tables()
        
        if tables:
            print(f"✅ Найдено {len(tables)} таблиц:")
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table}")
                
            # Тестирование получения схемы для первой таблицы
            if tables:
                first_table = tables[0]
                print(f"\n🔍 Получение схемы для таблицы: {first_table}")
                schema = db_manager.get_table_structure(first_table)
                
                if schema:
                    print(f"✅ Структура таблицы успешно получена:")
                    for col in schema:
                        pk_marker = " 🔑" if col['pk'] else ""
                        null_marker = " ❌" if col['notnull'] else " ✅"
                        print(f"  • {col['name']} ({col['type']}){pk_marker}{null_marker}")
                else:
                    print("❌ Не удалось получить структуру таблицы")
        else:
            print("⚠️  Таблицы не найдены или проблема с подключением")
            
        # Тестирование получения полной схемы
        print("\n🗄️ Получение полной схемы базы данных...")
        complete_schema = db_manager.get_database_schema()
        if complete_schema:
            print(f"✅ Полная схема получена: {len(complete_schema)} таблиц")
        else:
            print("❌ Не удалось получить полную схему")
            
    else:
        print("❌ Не удалось подключиться к базе данных!")
        print("\n🔧 Советы по устранению неполадок:")
        print("1. Проверьте учетные данные базы данных в файле .env")
        print("2. Убедитесь, что путь к базе данных правильный")
        print("3. Проверьте сетевое подключение к удаленному серверу")
        print("4. Убедитесь, что файл базы данных существует и доступен")
    
    # Очистка
    db_manager.disconnect()
    print("\n🔌 Подключение к базе данных закрыто")

if __name__ == "__main__":
    try:
        test_database_connection()
    except Exception as e:
        print(f"❌ Тест завершился с ошибкой: {e}")
        print("\n🔧 Убедитесь, что у вас есть:")
        print("1. Создан файл .env с вашей конфигурацией")
        print("2. Установлены все необходимые зависимости")
        print("3. Есть доступ к удаленной базе данных")
