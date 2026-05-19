from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class EnrollmentReadModel:
    """
    Денормализованная read-модель для записи на курс.
    Содержит данные из Enrollment + джойн с Course.
    """
    id: str
    student_id: str
    course_id: str
    course_title: str
    course_description: str
    
    progress_percent: int
    completed_lessons_count: int
    total_lessons: int
    is_completed: bool
    
    started_at: datetime
    completed_at: Optional[datetime]
    last_activity_at: datetime

@dataclass
class StudentProgressReadModel:
    """
    Read-модель для агрегированного прогресса студента по всем курсам.
    """
    student_id: str
    total_courses: int
    completed_courses: int
    average_progress: float
    enrollments: List[EnrollmentReadModel]