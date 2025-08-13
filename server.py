from flask import Flask
import os
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_bot():
    try:
        print("🚀 Начинаю запуск бота...")
        
        # Импортируем и запускаем бота
        print("📦 Импортирую модули бота...")
        from bot import setup_database, setup_handlers, bot
        
        print("🔧 Настройка базы данных...")
        # Настройка базы данных и обработчиков
        if setup_database():
            print("✅ База данных успешно подключена")
        else:
            print("⚠️ Подключение к базе данных не удалось")
        
        print("🔧 Настройка обработчиков команд...")
        setup_handlers()
        
        # Запуск бота в режиме polling
        print("🤖 Запуск Telegram бота в режиме polling...")
        print(f"🔑 Токен бота: {'УСТАНОВЛЕН' if bot.token else 'НЕ УСТАНОВЛЕН'}")
        
        bot.polling(none_stop=True)
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА при запуске бота: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Запуск Flask сервера на порту {port}")
    print(f"🤖 Бот работает в фоновом потоке")
    app.run(host='0.0.0.0', port=port)
