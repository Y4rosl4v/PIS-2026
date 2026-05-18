from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

class QuestionType(Enum):
    SINGLE_CHOICE = "SINGLE_CHOICE"
    TRUE_FALSE = "TRUE_FALSE"

@dataclass
class Question:
    """Вопрос теста"""
    id: str
    text: str
    question_type: QuestionType
    options: List[str]
    correct_answer: str
    
    def validate_answer(self, user_answer: str) -> bool:
        """Проверить ответ"""
        return user_answer == self.correct_answer

@dataclass
class Test:
    """Итоговый тест курса"""
    course_id: str
    questions: List[Question]
    passing_score: float = 80.0
    max_attempts: int = 3
    
    def __post_init__(self):
        if len(self.questions) < 1:
            raise ValueError("Тест должен содержать хотя бы 1 вопрос")
        if not (0 <= self.passing_score <= 100):
            raise ValueError("Проходной балл должен быть 0-100")
    
    def calculate_score(self, answers: Dict[str, str]) -> float:
        """Подсчитать балл"""
        if not self.questions:
            return 0.0
        
        correct = 0
        for question in self.questions:
            if question.id in answers and question.validate_answer(answers[question.id]):
                correct += 1
        
        return (correct / len(self.questions)) * 100