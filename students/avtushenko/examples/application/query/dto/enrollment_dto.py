from dataclasses import dataclass
from typing import List

@dataclass
class EnrollmentDTO:
    """DTO для чтения информации о прогрессе студента"""
    id: str
    student_id: str
    course_id: str
    progress_percent: int
    completed_lessons: List[str]
    is_completed: bool