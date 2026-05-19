from dataclasses import dataclass
from datetime import datetime

class DomainEvent:
    """Базовый класс для всех доменных событий"""
    pass

@dataclass(frozen=True)
class EnrollmentStartedEvent(DomainEvent):
    enrollment_id: str
    student_id: str
    course_id: str
    occurred_at: datetime = datetime.now()

@dataclass(frozen=True)
class LessonCompletedEvent(DomainEvent):
    enrollment_id: str
    lesson_id: str
    new_progress: int
    occurred_at: datetime = datetime.now()

@dataclass(frozen=True)
class TestPassedEvent(DomainEvent):
    enrollment_id: str
    lesson_id: str
    passed: bool
    occurred_at: datetime = datetime.now()

@dataclass(frozen=True)
class CourseCompletedEvent(DomainEvent):
    enrollment_id: str
    student_id: str
    course_id: str
    completed_at: datetime