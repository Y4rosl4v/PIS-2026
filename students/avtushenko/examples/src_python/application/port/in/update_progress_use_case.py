from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class UpdateProgressCommand:
    """DTO для обновления прогресса"""
    user_id: str
    course_id: str
    lesson_id: str
    video_percent: float

@dataclass
class UpdateProgressResult:
    """Результат обновления прогресса"""
    lesson_id: str
    video_percent: float
    is_completed: bool
    next_lesson_unlocked: bool

class UpdateProgressUseCase(ABC):
    """Входящий порт: Обновление прогресса просмотра"""
    
    @abstractmethod
    def execute(self, command: UpdateProgressCommand) -> UpdateProgressResult:
        """
        Обновляет прогресс просмотра урока
        :param command: Данные прогресса
        :return: Результат обновления
        :raises: LessonNotUnlockedException
        """
        pass