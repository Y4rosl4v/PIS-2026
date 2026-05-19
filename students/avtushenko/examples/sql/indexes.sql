-- Оптимизация запросов через индексы

-- Индексы для таблицы enrollments
CREATE INDEX IF NOT EXISTS idx_enrollments_student_course 
    ON enrollments(student_id, course_id);

CREATE INDEX IF NOT EXISTS idx_enrollments_course_progress 
    ON enrollments(course_id, (json_array_length(completed_lessons))) 
    WHERE total_lessons > 0;

CREATE INDEX IF NOT EXISTS idx_enrollments_completed 
    ON enrollments(course_id) WHERE completed_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_enrollments_updated 
    ON enrollments(updated_at DESC);

-- Индексы для таблицы lessons
CREATE INDEX IF NOT EXISTS idx_lessons_course_order 
    ON lessons(course_id, created_at);

-- Индексы для таблицы courses
CREATE INDEX IF NOT EXISTS idx_courses_rating 
    ON courses(rating DESC) WHERE rating IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_courses_created 
    ON courses(created_at DESC);

-- Таблица-кэш для быстрых запросов прогресса студентов
CREATE TABLE IF NOT EXISTS student_progress_cache (
    student_id VARCHAR(50) NOT NULL,
    course_id VARCHAR(50) NOT NULL,
    progress_percent INTEGER DEFAULT 0,
    completed_lessons JSONB DEFAULT '[]',
    completed_at TIMESTAMP,
    last_updated TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (student_id, course_id)
);

CREATE INDEX IF NOT EXISTS idx_progress_cache_student 
    ON student_progress_cache(student_id, progress_percent DESC);

CREATE INDEX IF NOT EXISTS idx_progress_cache_course 
    ON student_progress_cache(course_id, progress_percent DESC);