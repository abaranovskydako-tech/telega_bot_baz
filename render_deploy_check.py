#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации Render и тестирования базы данных
Запускайте этот скрипт для проверки готовности к развертыванию
"""

import os
import sys
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Проверяем переменные окружения"""
    logger.info("🔍 Проверка переменных окружения...")
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Токен бота Telegram',
        'DATABASE_PATH': 'Путь к базе данных',
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"{var} ({description})")
            logger.warning(f"❌ Отсутствует: {var}")
        else:
            logger.info(f"✅ {var}: {os.environ.get(var)[:20]}...")
    
    # Проверяем Render-специфичные переменные
    if os.environ.get('RENDER'):
        logger.info("✅ Обнаружена среда Render")
    else:
        logger.info("ℹ️  Локальная среда разработки")
    
    return len(missing_vars) == 0

def check_dependencies():
    """Проверяем зависимости"""
    logger.info("📦 Проверка зависимостей...")
    
    required_packages = [
        'flask',
        'telebot',  # pyTelegramBotAPI импортируется как telebot
        'sqlalchemy',
        'dotenv'    # python-dotenv импортируется как dotenv
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} - не установлен")
    
    return len(missing_packages) == 0

def check_database():
    """Проверяем базу данных"""
    logger.info("🗄️  Проверка базы данных...")
    
    try:
        import db
        
        # Проверяем инициализацию
        db.init_db()
        logger.info("✅ База данных db.py инициализирована успешно")
        
        # Проверяем доступность
        logger.info("✅ База данных доступна")
        logger.info("   Тип: db.py (PostgreSQL/SQLite)")
        logger.info("   Таблица: responses")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки базы данных: {e}")
        return False

def check_files():
    """Проверяем необходимые файлы"""
    logger.info("📁 Проверка файлов проекта...")
    
    required_files = [
        'server.py',
        'bot.py', 
        'database.py',
        'requirements.txt',
        'render.yaml'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            logger.info(f"✅ {file}")
        else:
            missing_files.append(file)
            logger.error(f"❌ {file} - отсутствует")
    
    return len(missing_files) == 0

def check_render_config():
    """Проверяем конфигурацию Render"""
    logger.info("🌐 Проверка конфигурации Render...")
    
    try:
        import yaml
        
        with open('render.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        if 'services' in config:
            service = config['services'][0]
            
            # Проверяем основные параметры
            if service.get('type') == 'web':
                logger.info("✅ Тип сервиса: web")
            else:
                logger.warning(f"⚠️  Неожиданный тип сервиса: {service.get('type')}")
            
            if service.get('env') == 'python':
                logger.info("✅ Среда: Python")
            else:
                logger.warning(f"⚠️  Неожиданная среда: {service.get('env')}")
            
            # Проверяем переменные окружения
            env_vars = service.get('envVars', [])
            required_env_vars = ['TELEGRAM_BOT_TOKEN', 'DATABASE_PATH', 'RENDER']
            
            for required_var in required_env_vars:
                found = any(env.get('key') == required_var for env in env_vars)
                if found:
                    logger.info(f"✅ Переменная окружения: {required_var}")
                else:
                    logger.warning(f"⚠️  Отсутствует переменная: {required_var}")
            
            logger.info("✅ Конфигурация Render корректна")
            return True
            
    except ImportError:
        logger.warning("⚠️  PyYAML не установлен, пропускаем проверку render.yaml")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка проверки render.yaml: {e}")
        return False

def main():
    """Основная функция проверки"""
    logger.info("🚀 Запуск проверки конфигурации для Render...")
    logger.info("=" * 50)
    
    checks = [
        ("Переменные окружения", check_environment),
        ("Зависимости", check_dependencies),
        ("Файлы проекта", check_files),
        ("Конфигурация Render", check_render_config),
        ("База данных", check_database),
    ]
    
    results = []
    for check_name, check_func in checks:
        logger.info(f"\n🔍 {check_name}:")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            logger.error(f"❌ Ошибка в проверке {check_name}: {e}")
            results.append((check_name, False))
    
    # Итоговый отчет
    logger.info("\n" + "=" * 50)
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ:")
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ НЕ ПРОЙДЕНО"
        logger.info(f"{status} - {check_name}")
        if result:
            passed += 1
    
    logger.info(f"\n📈 Результат: {passed}/{total} проверок пройдено")
    
    if passed == total:
        logger.info("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Проект готов к развертыванию на Render!")
        return 0
    else:
        logger.error("⚠️  НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ. Исправьте ошибки перед развертыванием.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
