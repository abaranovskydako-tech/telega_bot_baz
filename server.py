from flask import Flask
import os
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_bot():
    # Импортируем и запускаем бота
    from bot import setup_database, setup_handlers, bot as telegram_bot
    
    # Настройка базы данных и обработчиков
    if setup_database():
        print("✅ База данных успешно подключена")
    else:
        print("⚠️ Подключение к базе данных не удалось")
    
    setup_handlers()
    
    # Запуск бота в режиме polling
    print("🤖 Запуск Telegram бота в режиме polling...")
    telegram_bot.polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Запуск Flask сервера на порту {port}")
    print(f"🤖 Бот работает в фоновом потоке")
    app.run(host='0.0.0.0', port=port)
