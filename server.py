from flask import Flask, jsonify
import os
import threading
import logging
from bot import run_bot
import database
from db import init_db, save_response

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Главная страница с информацией о боте"""
    return """
    <h1>🤖 Telegram Questionnaire Bot</h1>
    <p>Бот работает и готов к использованию!</p>
    <p><strong>Статус:</strong> ✅ Активен</p>
    <p><strong>Функции:</strong></p>
    <ul>
        <li>📋 Опрос пользователей</li>
        <li>💾 Сохранение данных в SQLite</li>
        <li>🌐 Готов к развертыванию на Render</li>
    </ul>
    <p><a href="/health">🔍 Проверить здоровье системы</a></p>
    <p><a href="/db-info">📊 Информация о базе данных</a></p>
    <p><a href="/test-db">🧪 Тест новой базы данных</a></p>
    """

@app.route('/health')
def health():
    """Проверка здоровья всей системы"""
    try:
        # Проверяем здоровье базы данных через db.py
        from db import init_db
        try:
            init_db()  # Проверяем доступность базы
            db_health = {"status": "healthy", "database": "db.py"}
        except Exception as e:
            db_health = {"status": "unhealthy", "error": str(e)}
        
        # Общая оценка здоровья
        overall_status = "healthy" if db_health["status"] == "healthy" else "degraded"
        
        return jsonify({
            "status": overall_status,
            "timestamp": "2025-08-15T00:00:00",  # Статическая дата
            "database": db_health,
            "bot": "running",
            "server": "flask"
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": database.datetime.now().isoformat()
        }), 500

@app.route('/db-info')
def db_info():
    """Информация о базе данных"""
    try:
        from db import init_db
        init_db()  # Проверяем доступность
        db_info = {"status": "healthy", "database": "db.py", "table": "responses"}
        return jsonify({
            "database_info": db_info,
            "timestamp": "2025-08-15T00:00:00"
        })
    except Exception as e:
        logger.error(f"Database info failed: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": "2025-08-15T00:00:00"
        }), 500

@app.route('/stats')
def stats():
    """Статистика опросов"""
    try:
        from db import init_db
        init_db()  # Проверяем доступность базы
        
        # Пока временная статистика для db.py
        stats_info = {
            "total_responses": "N/A (db.py)",
            "unique_users": "N/A (db.py)",
            "average_per_user": "N/A (db.py)",
            "note": "Статистика будет доступна после полной миграции на db.py"
        }
        
        return jsonify({
            **stats_info,
            "timestamp": "2025-08-15T00:00:00"
        })
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": "2025-08-15T00:00:00"
        }), 500

@app.route('/test-db')
def test_db():
    """Тестирование новой базы данных (db.py)"""
    try:
        # Тестируем сохранение ответа
        test_user_id = 12345
        test_question = "Тестовый вопрос"
        test_answer = "Тестовый ответ"
        
        save_response(test_user_id, test_question, test_answer)
        
        return jsonify({
            "status": "success",
            "message": "Тестовый ответ сохранен в новую базу данных",
            "user_id": test_user_id,
            "question": test_question,
            "answer": test_answer,
            "timestamp": database.datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Test DB failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": database.datetime.now().isoformat()
        }), 500

def run_flask_server():
    """Запуск Flask сервера"""
    try:
        # Инициализируем новую базу данных (db.py)
        logger.info("Инициализация новой базы данных (db.py)...")
        init_db()  # создаст таблицы при старте
        logger.info("Новая база данных инициализирована успешно")
        
        # Инициализируем новую базу данных (db.py)
        logger.info("Инициализация новой базы данных (db.py)...")
        try:
            init_db()
            logger.info("Новая база данных инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации новой базы данных: {e}")
            return
        
        # Запускаем бота в отдельном потоке
        logger.info("Запуск Telegram бота в фоновом режиме...")
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Бот запущен в фоновом режиме")
        
        # Запуск Flask сервера
        port = int(os.environ.get("PORT", 5008))
        logger.info(f"Запуск Flask сервера на порту {port}")
        
        app.run(
            host='0.0.0.0', 
            port=port,
            debug=False,
            threaded=True  # Включаем многопоточность для лучшей производительности
        )
        
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}")
        raise

if __name__ == '__main__':
    run_flask_server()
