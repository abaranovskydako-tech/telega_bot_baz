from flask import Flask
import os
import threading
import bot  # Импортируй свой файл с ботом

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_bot():
    bot.main()  # Здесь должна быть функция, которая запускает бота

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
