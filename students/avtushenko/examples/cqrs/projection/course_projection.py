from sqlalchemy.orm import Session
from sqlalchemy import text

class CourseProjection:
    """
    Проекция для обновления денормализованных данных о курсах.
    Обновляет материализованное представление course_statistics_mv.
    """
    
    def __init__(self, db_session: Session):
        self._db = db_session
    
    def refresh_course_statistics(self, course_id: str) -> None:
        """Обновить статистику для конкретного курса"""
        # Обновляем материализованное представление
        sql = text("""
            INSERT INTO course_statistics_mv (course_id, total_enrollments, completed_enrollments, avg_progress, avg_rating, last_updated)
            VALUES (
                :course_id,
                COALESCE((
                    SELECT COUNT(*) FROM enrollments 
                    WHERE course_id = :course_id
                ), 0),
                COALESCE((
                    SELECT COUNT(*) FROM enrollments 
                    WHERE course_id = :course_id AND completed_at IS NOT NULL
                ), 0),
                COALESCE((
                    SELECT AVG(
                        CASE 
                            WHEN total_lessons > 0 
                            THEN (json_array_length(completed_lessons)::float / total_lessons) * 100
                            ELSE 0 
                        END
                    ) FROM enrollments 
                    WHERE course_id = :course_id
                ), 0),
                COALESCE((
                    SELECT AVG(rating) FROM courses WHERE id = :course_id
                ), 0),
                NOW()
            )
            ON CONFLICT (course_id) DO UPDATE SET
                total_enrollments = EXCLUDED.total_enrollments,
                completed_enrollments = EXCLUDED.completed_enrollments,
                avg_progress = EXCLUDED.avg_progress,
                avg_rating = EXCLUDED.avg_rating,
                last_updated = EXCLUDED.last_updated
        """)
        
        self._db.execute(sql, {"course_id": course_id})
        self._db.commit()
    
    def refresh_course_statistics_by_enrollment(self, enrollment_id: str) -> None:
        """Обновить статистику курса по ID записи"""
        sql = text("""
            SELECT course_id FROM enrollments WHERE id = :enrollment_id
        """)
        result = self._db.execute(sql, {"enrollment_id": enrollment_id}).first()
        
        if result:
            self.refresh_course_statistics(result[0])
    
    def refresh_all_statistics(self) -> None:
        """Полное обновление материализованного представления"""
        sql = text("REFRESH MATERIALIZED VIEW CONCURRENTLY course_statistics_mv")
        self._db.execute(sql)
        self._db.commit()