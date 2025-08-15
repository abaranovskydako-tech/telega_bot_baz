# 🔌 Подключение к БД в DBeaver (PostgreSQL)

## 📋 Параметры подключения к Render PostgreSQL

**Host:** `dpg-d2eppj3ipnbc73a9j400-a.oregon-postgres.render.com`  
**Port:** `5432`  
**Database:** `telega_db`  
**Username:** `telega_db_user`  
**Password:** `DsPFD2TL02eWdqsTuNqGWxeX2faromvj`  
**SSL:** `require`

## 🚀 1. Установка DBeaver (если не установлен)

### macOS:
```bash
brew install --cask dbeaver-community
```

### Windows:
- Скачать с [dbeaver.io](https://dbeaver.io/download/)
- Установить как обычное приложение

### Linux:
```bash
# Ubuntu/Debian
sudo apt-get install dbeaver-ce

# CentOS/RHEL
sudo yum install dbeaver-ce
```

## 🔗 2. Создание подключения в DBeaver

### Шаг 1: Новое подключение
1. Запустите DBeaver
2. Нажмите **"Новое подключение"** (значок +)
3. Выберите **PostgreSQL** из списка

### Шаг 2: Основные параметры
```
Server Host: dpg-d2eppj3ipnbc73a9j400-a.oregon-postgres.render.com
Port: 5432
Database: telega_db
Username: telega_db_user
Password: DsPFD2TL02eWdqsTuNqGWxeX2faromvj
```

### Шаг 3: SSL настройки
1. Перейдите на вкладку **"SSL"**
2. Установите **"Use SSL"** = `true`
3. **"SSL Mode"** = `require`
4. **"SSL Factory"** = `org.postgresql.ssl.NonValidatingFactory`

### Шаг 4: Дополнительные настройки
1. Перейдите на вкладку **"Driver properties"**
2. Добавьте параметр:
   - **Property:** `sslmode`
   - **Value:** `require`

## 🧪 3. Тестирование подключения

### Проверка соединения:
1. Нажмите **"Test Connection"**
2. Должно появиться: **"Connected"** ✅
3. Если ошибка - проверьте SSL настройки

### Первый запрос:
```sql
-- Проверка таблицы
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Должно показать: survey_responses
```

## 📊 4. Выполнение SQL запросов

### Основной запрос для проверки данных:
```sql
-- Последние 50 записей анкеты
SELECT id, user_id, full_name, birth_date, citizenship, created_at
FROM survey_responses
ORDER BY id DESC
LIMIT 50;
```

### Дополнительные запросы:
```sql
-- Количество записей
SELECT COUNT(*) as total_records FROM survey_responses;

-- Уникальные пользователи
SELECT COUNT(DISTINCT user_id) as unique_users FROM survey_responses;

-- Последние 10 записей с деталями
SELECT 
    id,
    user_id,
    full_name,
    birth_date,
    citizenship,
    created_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))/3600 as hours_ago
FROM survey_responses
ORDER BY created_at DESC
LIMIT 10;
```

## 🔍 5. Структура таблицы survey_responses

```sql
-- Просмотр структуры таблицы
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'survey_responses'
ORDER BY ordinal_position;
```

**Ожидаемые поля:**
- `id` - INTEGER (Primary Key)
- `user_id` - INTEGER (Telegram User ID)
- `full_name` - TEXT (ФИО пользователя)
- `birth_date` - TEXT (Дата рождения)
- `citizenship` - TEXT (Гражданство)
- `created_at` - TIMESTAMP (Время создания)

## 🚨 6. Устранение неполадок

### Ошибка "Connection refused":
- Проверьте правильность Host и Port
- Убедитесь, что сервис на Render запущен

### Ошибка "SSL required":
- Проверьте SSL настройки
- Убедитесь, что `sslmode=require`

### Ошибка "Authentication failed":
- Проверьте Username и Password
- Убедитесь, что БД существует и доступна

### Ошибка "Database does not exist":
- Проверьте название Database
- Убедитесь, что БД создана на Render

## 📱 7. Проверка через веб-интерфейс

Перед подключением в DBeaver проверьте доступность БД:

```
https://<имя-сервиса>.onrender.com/_diag/db
```

**Ожидаемый ответ:**
```json
{
  "ok": true,
  "dialect": "postgresql",
  "count": 5,
  "last": {
    "id": 5,
    "user_id": 123456789,
    "full_name": "Иванов Иван",
    "birth_date": "1990-03-15",
    "citizenship": "Россия",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

## ✅ 8. Чек-лист подключения

- [ ] DBeaver установлен
- [ ] Создано подключение к PostgreSQL
- [ ] SSL настроен (require)
- [ ] Тест подключения успешен
- [ ] Таблица `survey_responses` видна
- [ ] SQL запросы выполняются
- [ ] Данные отображаются корректно

---

**🎯 Цель:** Проверить, что данные из Telegram-бота корректно сохраняются в PostgreSQL на Render и доступны для просмотра через DBeaver.
