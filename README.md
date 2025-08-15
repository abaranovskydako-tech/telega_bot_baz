# 🤖 Проект Telegram-бота (анкета)

Telegram бот для проведения опросов с интеграцией SQLite/PostgreSQL базы данных, оптимизированный для развертывания на Render.

## ✨ Возможности

- 📋 Интерактивные опросы пользователей
- 💾 Сохранение данных в SQLite (локально) или PostgreSQL (облако)
- 🌐 Веб-интерфейс для мониторинга
- 🔍 Health check endpoints
- 📊 Статистика опросов
- 🚀 Готов к развертыванию на Render

## 🏗️ Архитектура

- **Telegram Bot** - основной функционал опросов
- **Flask Server** - веб-интерфейс и API
- **SQLAlchemy ORM** - универсальный слой для работы с БД
- **SQLite/PostgreSQL** - поддержка локальной и облачной БД
- **Render Integration** - оптимизация для облачной платформы

## 🗄️ Два режима работы БД

- **Локально (SQLite)** — без переменной DATABASE_URL данные пишутся в файл `telega.db`/`questionnaire.db`.
- **Облако (PostgreSQL на Render)** — при наличии переменной `DATABASE_URL` вида `postgresql+pg8000://...` запись идёт в удалённую БД.

## 🚀 Запуск локально (SQLite)

1. **Создай `.env` и укажи:**
   ```
   TELEGRAM_BOT_TOKEN=...твой токен...
   ```
   (строку DATABASE_URL не добавляй для локального режима).

2. **Установи зависимости и запусти:**
   ```bash
   pip install -r requirements.txt
   python server.py
   ```

3. **Напиши боту `/start`, заполни анкету.**

4. **Открой файл `questionnaire.db` (или `telega.db`) любым GUI (DB Browser for SQLite) и проверь таблицу `survey_responses`.**

## ☁️ Развёртывание на Render (PostgreSQL)

1. **В сервисе укажи переменные окружения:**
   - `TELEGRAM_BOT_TOKEN=...`
   - `DATABASE_URL=postgresql+pg8000://<user>:<pass>@<host>:5432/telega_db` (без `sslmode`, SSL добавляется через код).

2. **Нажми **Manual Deploy → Clear build cache & Deploy latest commit**.**

3. **После старта бот отвечает, сервис доступен на `https://<имя-сервиса>.onrender.com`.**

4. **Диагностика БД через браузер: открой**
   ```
   https://<имя-сервиса>.onrender.com/_diag/db
   ```
   Должно показать `{"ok": true, "dialect": "postgresql", "count": ... , "last": {...}}`.

## 📊 Просмотр/экспорт данных из PostgreSQL

**Подключение:**
- Host: `dpg-d2eppj3ipnbc73a9j400-a.oregon-postgres.render.com`
- Port: `5432`
- Database: `telega_db`
- User: `telega_db_user`
- Password: см. `DATABASE_URL`
- SSL: require

**Запрос:**
```sql
\i docs/sql/queries.sql
```

## 🔧 Структура проекта

```
VCc01/
├── bot.py              # Telegram бот
├── server.py           # Flask веб-сервер
├── db.py               # SQLAlchemy слой БД
├── database.py         # Старый слой БД (SQLite)
├── requirements.txt    # Зависимости
├── render.yaml         # Конфигурация Render
├── docs/
│   └── sql/
│       └── queries.sql # SQL запросы для проверки
└── README.md           # Этот файл
```

## 📋 API Endpoints

- **`/`** - Главная страница
- **`/health`** - Проверка здоровья системы
- **`/db-info`** - Информация о базе данных
- **`/stats`** - Статистика опросов
- **`/_diag/db`** - Диагностика БД survey_responses

## 🧪 Тестирование

1. **Локально:** Запусти `python server.py` и открой `http://localhost:5000/_diag/db`
2. **На Render:** Открой `https://<имя-сервиса>.onrender.com/_diag/db`

## 📝 Чек-лист для проверки

- [ ] Бот отвечает на команду `/start`
- [ ] Анкета заполняется и сохраняется
- [ ] Локально: данные в `questionnaire.db` (SQLite)
- [ ] Облако: данные в PostgreSQL через `/_diag/db`
- [ ] Диагностика показывает `{"ok": true, "dialect": "..."}`
- [ ] Таблица `survey_responses` содержит записи

## 🚨 Устранение неполадок

- **Ошибка подключения к БД:** Проверь переменные окружения
- **SSL ошибки:** Убедись, что `DATABASE_URL` не содержит `sslmode`
- **Бот не отвечает:** Проверь `TELEGRAM_BOT_TOKEN`

---

**🎯 Готов к проверке!** Все компоненты работают через SQLAlchemy слой, поддерживают SQLite и PostgreSQL, имеют диагностические эндпоинты.
