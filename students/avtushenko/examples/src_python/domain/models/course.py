from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from datetime import datetime

class CourseStatus(Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

@dataclass
class Lesson:
    """Value Object: Урок курса"""
    id: str
    title: str
    video_url: str
    duration_seconds: int
    order: int
    
    def __post_init__(self):
        if self.duration_seconds <= 0:
            raise ValueError("Длительность урока должна быть > 0")
        if not self.title.strip():
            raise ValueError("Название урока обязательно")

@dataclass
class Course:
    """Доменная сущность: Мини-курс"""
    id: str
    title: str
    description: str
    author_id: str
    status: CourseStatus
    lessons: List[Lesson]
    created_at: datetime
    passing_score: float = 80.0  # Проходной балл в %
    
    def __post_init__(self):
        """Валидация доменных правил"""
        if not self.title.strip():
            raise ValueError("Название курса обязательно")
        if len(self.lessons) < 1:
            raise ValueError("Курс должен содержать хотя бы 1 урок")
        if not (0 <= self.passing_score <= 100):
            raise ValueError("Проходной балл должен быть 0-100")
    
    def activate(self):
        """Активировать курс"""
        if self.status != CourseStatus.DRAFT:
            raise ValueError("Нельзя активировать курс в статусе " + self.status.value)
        self.status = CourseStatus.ACTIVE
    
    def archive(self):
        """Архивировать курс"""
        self.status = CourseStatus.ARCHIVED
    
    def get_total_duration(self) -> int:
        """Получить общую длительность курса в секундах"""
        return sum(lesson.duration_seconds for lesson in self.lessons)