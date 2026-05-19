from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.cqrs.read_model import CourseReadModel, CourseSummaryReadModel

class CourseReadRepository:
    """
    Репозиторий для чтения денормализованных данных о курсах.
    Использует материализованные представления и оптимизированные запросы.
    """
    
    def __init__(self, db_session: Session):
        self._db = db_session
    
    def find_by_id(self, course_id: str) -> Optional[CourseReadModel]:
        """Найти курс по ID (с денормализованными данными)"""
        sql = text("""
            SELECT 
                c.id,
                c.title,
                c.description,
                c.rating,
                c.created_at,
                c.updated_at,
                COALESCE(l.lesson_count, 0) as total_lessons,
                COALESCE(e.total_students, 0) as total_students,
                COALESCE(e.completed_students, 0) as completed_students,
                COALESCE(e.avg_progress, 0) as average_progress
            FROM courses c
            LEFT JOIN (
                SELECT course_id, COUNT(*) as lesson_count
                FROM lessons
                GROUP BY course_id
            ) l ON c.id = l.course_id
            LEFT JOIN (
                SELECT 
                    course_id,
                    COUNT(*) as total_students,
                    COUNT(CASE WHEN completed_at IS NOT NULL THEN 1 END) as completed_students,
                    AVG(CASE 
                        WHEN total_lessons > 0 
                        THEN (json_array_length(completed_lessons)::float / total_lessons) * 100
                        ELSE 0 
                    END) as avg_progress
                FROM enrollments
                GROUP BY course_id
            ) e ON c.id = e.course_id
            WHERE c.id = :course_id
        """)
        
        result = self._db.execute(sql, {"course_id": course_id}).first()
        if not result:
            return None
        
        return CourseReadModel(
            id=result[0],
            title=result[1],
            description=result[2],
            rating=result[3],
            total_lessons=result[6],
            total_students=result[7],
            completed_students=result[8],
            average_progress=result[9],
            created_at=result[4],
            updated_at=result[5]
        )
    
    def find_all_summaries(self, limit: int = 50, offset: int = 0) -> List[CourseSummaryReadModel]:
        """Получить список курсов с агрегированными данными (оптимизировано)"""
        sql = text("""
            SELECT 
                c.id,
                c.title,
                c.rating,
                COALESCE(e.total_students, 0) as total_students,
                COALESCE(e.avg_progress, 0) as average_progress
            FROM courses c
            LEFT JOIN (
                SELECT 
                    course_id,
                    COUNT(*) as total_students,
                    AVG(CASE 
                        WHEN total_lessons > 0 
                        THEN (json_array_length(completed_lessons)::float / total_lessons) * 100
                        ELSE 0 
                    END) as avg_progress
                FROM enrollments
                GROUP BY course_id
            ) e ON c.id = e.course_id
            ORDER BY COALESCE(c.rating, 0) DESC
            LIMIT :limit OFFSET :offset
        """)
        
        results = self._db.execute(sql, {"limit": limit, "offset": offset}).fetchall()
        
        return [
            CourseSummaryReadModel(
                id=r[0],
                title=r[1],
                rating=r[2],
                total_students=r[3],
                average_progress=r[4]
            )
            for r in results
        ]
    
    def find_top_rated(self, limit: int = 10) -> List[CourseSummaryReadModel]:
        """Найти топ курсов по рейтингу"""
        return self.find_all_summaries(limit=limit)
    
    def find_most_popular(self, limit: int = 10) -> List[CourseSummaryReadModel]:
        """Найти самые популярные курсы (по количеству студентов)"""
        sql = text("""
            SELECT 
                c.id,
                c.title,
                c.rating,
                COUNT(e.id) as total_students,
                COALESCE(AVG(
                    CASE 
                        WHEN e.total_lessons > 0 
                        THEN (json_array_length(e.completed_lessons)::float / e.total_lessons) * 100
                        ELSE 0 
                    END), 0) as avg_progress
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY c.id
            ORDER BY total_students DESC
            LIMIT :limit
        """)
        
        results = self._db.execute(sql, {"limit": limit}).fetchall()
        
        return [
            CourseSummaryReadModel(
                id=r[0],
                title=r[1],
                rating=r[2],
                total_students=r[3],
                average_progress=r[4]
            )
            for r in results
        ]
    
    def get_course_statistics(self, course_id: str) -> dict:
        """Получить статистику по курсу (оптимизировано через материализованное представление)"""
        # Используем материализованное представление для быстрых агрегаций
        sql = text("""
            SELECT * FROM course_statistics_mv
            WHERE course_id = :course_id
        """)
        
        result = self._db.execute(sql, {"course_id": course_id}).first()
        if not result:
            return {}
        
        return {
            "course_id": result[0],
            "total_enrollments": result[1],
            "completed_enrollments": result[2],
            "avg_progress": result[3],
            "avg_rating": result[4],
            "last_updated": result[5]
        }