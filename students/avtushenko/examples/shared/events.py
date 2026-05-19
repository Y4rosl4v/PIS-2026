from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DomainEvent:
    """Базовый класс для всех событий"""
    occurred_at: datetime

@dataclass
class CourseCreatedEvent(DomainEvent):
    """Курс создан"""
    course_id: str
    title: str
    occurred_at: datetime

@dataclass
class StudentEnrolledEvent(DomainEvent):
    """Студент записался на курс"""
    enrollment_id: str
    student_id: str
    course_id: str
    course_title: str
    occurred_at: datetime

@dataclass
class LessonCompletedEvent(DomainEvent):
    """Урок завершён"""
    enrollment_id: str
    student_id: str
    course_id: str
    lesson_id: str
    new_progress: int
    occurred_at: datetime

@dataclass
class CourseCompletedEvent(DomainEvent):
    """Курс завершён"""
    enrollment_id: str
    student_id: str
    course_id: str
    course_title: str
    completed_at: datetime

@dataclass
class TestPassedEvent(DomainEvent):
    """Тест пройден"""
    enrollment_id: str
    student_id: str
    course_id: str
    lesson_id: str
    passed: bool
    occurred_at: datetime