from flask import Flask
import os
import threading
import bot  # Импортируй свой файл с ботом

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_bot():
    # Импортируем и запускаем бота
    from bot import setup_database, setup_handlers
    
    # Настройка базы данных и обработчиков
    if bot.setup_database():
        print("✅ Database connected successfully")
    else:
        print("⚠️ Database connection failed")
    
    bot.setup_handlers()
    
    # Запуск бота в режиме polling
    bot.bot.polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
