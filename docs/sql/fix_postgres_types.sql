-- Исправление типов данных для миграции из SQLite
-- user_id должен быть BIGINT для хранения больших Telegram ID

-- Изменяем тип user_id на BIGINT
ALTER TABLE survey_responses ALTER COLUMN user_id TYPE BIGINT;

-- Проверяем результат
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'survey_responses'
ORDER BY ordinal_position;
