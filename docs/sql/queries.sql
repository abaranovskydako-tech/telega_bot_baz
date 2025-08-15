-- Последние 50 записей анкеты
SELECT id, user_id, full_name, birth_date, citizenship, created_at
FROM survey_responses
ORDER BY id DESC
LIMIT 50;
