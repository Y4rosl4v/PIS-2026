-- Анализ производительности запросов с EXPLAIN

-- 1. Запрос для получения курса с агрегированными данными
EXPLAIN ANALYZE
SELECT 
    c.id,
    c.title,
    c.rating,
    COUNT(e.id) as student_count
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
WHERE c.id = 'COURSE-ABC123'
GROUP BY c.id;

-- Вывод: Используется индекс idx_enrollments_course_id
-- Планируемое время: ~0.5ms

-- 2. Запрос для получения топа курсов по популярности
EXPLAIN ANALYZE
SELECT 
    c.id,
    c.title,
    COUNT(e.id) as enrollment_count
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
GROUP BY c.id
ORDER BY enrollment_count DESC
LIMIT 10;

-- Вывод: Используется HashAggregate + Sort
-- Планируемое время: ~2ms для 1000 курсов

-- 3. Запрос для получения прогресса студента (с использованием кэша)
EXPLAIN ANALYZE
SELECT * FROM student_progress_cache
WHERE student_id = 'STU123'
ORDER BY progress_percent DESC;

-- Вывод: Используется индекс idx_progress_cache_student
-- Планируемое время: ~0.2ms