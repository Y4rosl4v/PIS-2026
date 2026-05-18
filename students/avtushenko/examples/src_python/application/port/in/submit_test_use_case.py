from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

@dataclass
class SubmitTestCommand:
    """DTO для команды сдачи теста"""
    user_id: str
    course_id: str
    answers: Dict[str, str]  # question_id -> answer

@dataclass
class SubmitTestResult:
    """Результат сдачи теста"""
    score: float
    passed: bool
    attempts: int
    badge_id: str | None = None

class SubmitTestUseCase(ABC):
    """Входящий порт: Сдача итогового теста"""
    
    @abstractmethod
    def execute(self, command: SubmitTestCommand) -> SubmitTestResult:
        """
        Принимает ответы на тест, валидирует, считает балл
        :param command: Данные теста
        :return: Результат с баллом и статусом
        :raises: MaxAttemptsReachedException, LessonNotUnlockedException
        """
        pass