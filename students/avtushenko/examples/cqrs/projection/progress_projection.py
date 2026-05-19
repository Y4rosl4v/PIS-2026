from sqlalchemy.orm import Session
from sqlalchemy import text
from app.domain.events import EnrollmentStartedEvent, LessonCompletedEvent, CourseCompletedEvent

class ProgressProjection:
    """
    Проекция для обновления денормализованных данных о прогрессе студентов.
    Обновляет таблицу student_progress_cache для быстрых запросов.
    """
    
    def __init__(self, db_session: Session):
        self._db = db_session
    
    def on_enrollment_started(self, event: EnrollmentStartedEvent) -> None:
        """Создание записи в кэше прогресса при старте"""
        sql = text("""
            INSERT INTO student_progress_cache (student_id, course_id, progress_percent, completed_lessons, last_updated)
            VALUES (:student_id, :course_id, 0, '[]', NOW())
            ON CONFLICT (student_id, course_id) DO UPDATE SET
                progress_percent = EXCLUDED.progress_percent,
                last_updated = EXCLUDED.last_updated
        """)
        
        self._db.execute(sql, {
            "student_id": event.student_id,
            "course_id": event.course_id
        })
        self._db.commit()
    
    def on_lesson_completed(self, event: LessonCompletedEvent) -> None:
        """Обновление кэша прогресса при завершении урока"""
        # Получаем актуальный прогресс из enrollment
        sql_get = text("""
            SELECT 
                student_id,
                course_id,
                CASE 
                    WHEN total_lessons > 0 
                    THEN (json_array_length(completed_lessons)::float / total_lessons) * 100
                    ELSE 0 
                END as progress_percent,
                completed_lessons
            FROM enrollments
            WHERE id = :enrollment_id
        """)
        
        result = self._db.execute(sql_get, {"enrollment_id": event.enrollment_id}).first()
        
        if result:
            sql_update = text("""
                INSERT INTO student_progress_cache (student_id, course_id, progress_percent, completed_lessons, last_updated)
                VALUES (:student_id, :course_id, :progress, :completed_lessons, NOW())
                ON CONFLICT (student_id, course_id) DO UPDATE SET
                    progress_percent = EXCLUDED.progress_percent,
                    completed_lessons = EXCLUDED.completed_lessons,
                    last_updated = EXCLUDED.last_updated
            """)
            
            self._db.execute(sql_update, {
                "student_id": result[0],
                "course_id": result[1],
                "progress": result[2],
                "completed_lessons": result[3]
            })
            self._db.commit()
    
    def on_course_completed(self, event: CourseCompletedEvent) -> None:
        """Отметка о завершении курса в кэше"""
        sql = text("""
            UPDATE student_progress_cache
            SET completed_at = NOW(), last_updated = NOW()
            WHERE student_id = :student_id AND course_id = :course_id
        """)
        
        self._db.execute(sql, {
            "student_id": event.student_id,
            "course_id": event.course_id
        })
        self._db.commit()