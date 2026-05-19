from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.cqrs.read_model import EnrollmentReadModel, StudentProgressReadModel

class ProgressReadRepository:
    """
    Репозиторий для чтения денормализованных данных о прогрессе студентов.
    """
    
    def __init__(self, db_session: Session):
        self._db = db_session
    
    def find_by_student_and_course(self, student_id: str, course_id: str) -> Optional[EnrollmentReadModel]:
        """Найти прогресс студента по конкретному курсу"""
        sql = text("""
            SELECT 
                e.id,
                e.student_id,
                e.course_id,
                c.title as course_title,
                c.description as course_description,
                CASE 
                    WHEN e.total_lessons > 0 
                    THEN (json_array_length(e.completed_lessons)::float / e.total_lessons) * 100
                    ELSE 0 
                END as progress_percent,
                json_array_length(e.completed_lessons) as completed_count,
                e.total_lessons,
                CASE 
                    WHEN e.completed_at IS NOT NULL THEN TRUE 
                    ELSE FALSE 
                END as is_completed,
                e.started_at,
                e.completed_at,
                e.updated_at as last_activity_at
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = :student_id AND e.course_id = :course_id
        """)
        
        result = self._db.execute(sql, {
            "student_id": student_id,
            "course_id": course_id
        }).first()
        
        if not result:
            return None
        
        return EnrollmentReadModel(
            id=result[0],
            student_id=result[1],
            course_id=result[2],
            course_title=result[3],
            course_description=result[4],
            progress_percent=result[5],
            completed_lessons_count=result[6],
            total_lessons=result[7],
            is_completed=result[8],
            started_at=result[9],
            completed_at=result[10],
            last_activity_at=result[11]
        )
    
    def find_by_student(self, student_id: str) -> StudentProgressReadModel:
        """Найти агрегированный прогресс студента по всем курсам"""
        sql = text("""
            WITH student_enrollments AS (
                SELECT 
                    e.course_id,
                    e.completed_at IS NOT NULL as is_completed,
                    CASE 
                        WHEN e.total_lessons > 0 
                        THEN (json_array_length(e.completed_lessons)::float / e.total_lessons) * 100
                        ELSE 0 
                    END as progress,
                    c.title,
                    c.description
                FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                WHERE e.student_id = :student_id
            )
            SELECT 
                :student_id as student_id,
                COUNT(*) as total_courses,
                SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) as completed_courses,
                COALESCE(AVG(progress), 0) as avg_progress,
                json_agg(
                    json_build_object(
                        'course_id', course_id,
                        'course_title', title,
                        'progress', progress,
                        'is_completed', is_completed
                    )
                ) as enrollments
            FROM student_enrollments
        """)
        
        result = self._db.execute(sql, {"student_id": student_id}).first()
        
        if not result or result[4] is None:
            return StudentProgressReadModel(
                student_id=student_id,
                total_courses=0,
                completed_courses=0,
                average_progress=0.0,
                enrollments=[]
            )
        
        enrollments_data = result[4]
        enrollments = []
        for e in enrollments_data:
            enrollments.append(EnrollmentReadModel(
                id="",  # Not needed for summary
                student_id=student_id,
                course_id=e["course_id"],
                course_title=e["course_title"],
                course_description="",
                progress_percent=e["progress"],
                completed_lessons_count=0,
                total_lessons=0,
                is_completed=e["is_completed"],
                started_at=None,
                completed_at=None,
                last_activity_at=None
            ))
        
        return StudentProgressReadModel(
            student_id=student_id,
            total_courses=result[1],
            completed_courses=result[2],
            average_progress=result[3],
            enrollments=enrollments
        )
    
    def find_all_active_students(self, min_progress: int = 0) -> List[dict]:
        """Найти всех активных студентов (с прогрессом > min_progress)"""
        sql = text("""
            SELECT 
                e.student_id,
                COUNT(DISTINCT e.course_id) as enrolled_courses,
                AVG(CASE 
                    WHEN e.total_lessons > 0 
                    THEN (json_array_length(e.completed_lessons)::float / e.total_lessons) * 100
                    ELSE 0 
                END) as avg_progress,
                MAX(e.updated_at) as last_activity
            FROM enrollments e
            GROUP BY e.student_id
            HAVING AVG(CASE 
                    WHEN e.total_lessons > 0 
                    THEN (json_array_length(e.completed_lessons)::float / e.total_lessons) * 100
                    ELSE 0 
                END) >= :min_progress
            ORDER BY last_activity DESC
        """)
        
        results = self._db.execute(sql, {"min_progress": min_progress}).fetchall()
        
        return [
            {
                "student_id": r[0],
                "enrolled_courses": r[1],
                "avg_progress": r[2],
                "last_activity": r[3]
            }
            for r in results
        ]