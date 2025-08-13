# Telegram Questionnaire Bot

Telegram бот для проведения опросов и сбора данных.

## 🚀 Развертывание на Render

### 1. Подготовка
- Убедитесь, что у вас есть токен Telegram бота от @BotFather
- Создайте аккаунт на [Render.com](https://render.com)

### 2. Переменные окружения
В Render Dashboard установите:
- `TELEGRAM_BOT_TOKEN` - ваш токен бота
- `DATABASE_PATH` - путь к базе данных (по умолчанию: ./questionnaire.db)
- `DB_USERNAME` - имя пользователя БД (если требуется)
- `DB_PASSWORD` - пароль БД (если требуется)

### 3. Развертывание
1. Подключите ваш Git репозиторий к Render
2. Выберите ветку для развертывания
3. Render автоматически определит Python проект
4. Нажмите "Deploy"

### 4. Команды
- Build: `pip install -r requirements.txt`
- Start: `python bot.py`

## 📁 Структура проекта
- `bot.py` - основной файл бота
- `database.py` - управление базой данных
- `render.yaml` - конфигурация Render
- `requirements.txt` - зависимости Python

## 🔧 Локальная разработка
1. Скопируйте `env.example` в `.env`
2. Заполните `TELEGRAM_BOT_TOKEN`
3. Установите зависимости: `pip install -r requirements.txt`
4. Запустите: `python bot.py`
