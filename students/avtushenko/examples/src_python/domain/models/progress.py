from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class ProgressStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class LessonProgress:
    """Progress урока"""
    lesson_id: str
    video_percent: float = 0.0
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not (0 <= self.video_percent <= 100):
            raise ValueError("Процент просмотра должен быть 0-100")
    
    def update_progress(self, percent: float):
        """Обновить прогресс просмотра"""
        if not (0 <= percent <= 100):
            raise ValueError("Процент должен быть 0-100")
        self.video_percent = max(self.video_percent, percent)  # Монотонный рост
        if self.video_percent == 100 and not self.completed_at:
            self.completed_at = datetime.utcnow()

@dataclass
class CourseProgress:
    """Доменная сущность: Прогресс обучения"""
    id: str
    user_id: str
    course_id: str
    status: ProgressStatus
    lesson_progresses: dict[str, LessonProgress] = field(default_factory=dict)
    test_attempts: int = 0
    final_score: Optional[float] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def start(self):
        """Начать обучение"""
        if self.status != ProgressStatus.NOT_STARTED:
            raise ValueError("Курс уже начат")
        self.status = ProgressStatus.IN_PROGRESS
    
    def complete(self, score: float):
        """Завершить курс с тестом"""
        self.test_attempts += 1
        self.final_score = score
        if score >= 80:
            self.status = ProgressStatus.COMPLETED
        else:
            self.status = ProgressStatus.FAILED
        self.completed_at = datetime.utcnow()
    
    def is_lesson_unlocked(self, lesson_id: str) -> bool:
        """Проверить, разблокирован ли урок"""
        if not self.lesson_progresses:
            return True  # Первый урок всегда открыт
        
        # Урок разблокирован, если предыдущий просмотрен на 100%
        lesson_ids = list(self.lesson_progresses.keys())
        if lesson_id not in lesson_ids:
            return False
        
        idx = lesson_ids.index(lesson_id)
        if idx == 0:
            return True
        
        prev_lesson = self.lesson_progresses[lesson_ids[idx - 1]]
        return prev_lesson.video_percent == 100