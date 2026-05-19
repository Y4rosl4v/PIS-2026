-- Материализованное представление для статистики курсов
-- Обновляется через проекции при изменении данных

DROP MATERIALIZED VIEW IF EXISTS course_statistics_mv CASCADE;

CREATE MATERIALIZED VIEW course_statistics_mv AS
SELECT 
    c.id AS course_id,
    COUNT(DISTINCT e.id) AS total_enrollments,
    COUNT(DISTINCT CASE WHEN e.completed_at IS NOT NULL THEN e.id END) AS completed_enrollments,
    COALESCE(AVG(
        CASE 
            WHEN e.total_lessons > 0 
            THEN (json_array_length(e.completed_lessons)::float / e.total_lessons) * 100
            ELSE 0 
        END
    ), 0) AS avg_progress,
    COALESCE(AVG(c.rating), 0) AS avg_rating,
    NOW() AS last_updated
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
GROUP BY c.id;

CREATE UNIQUE INDEX idx_course_stats_course_id ON course_statistics_mv(course_id);

-- Функция для автоматического обновления материализованного представления
CREATE OR REPLACE FUNCTION refresh_course_statistics()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY course_statistics_mv;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;