from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class TestQuestion:
    """Value Object: Вопрос теста"""
    text: str
    options: List[str]
    correct_option_index: int

    def __post_init__(self):
        if not self.text or not self.text.strip():
            raise ValueError("Question text cannot be empty")

        if len(self.options) < 2:
            raise ValueError("Question must have at least 2 options")

        if self.correct_option_index < 0 or self.correct_option_index >= len(self.options):
            raise ValueError("Correct option index out of range")

        # Проверка на дубликаты опций
        if len(set(self.options)) != len(self.options):
            raise ValueError("Options must be unique")

    def is_correct(self, selected_index: int) -> bool:
        """Проверить, правильный ли ответ"""
        return selected_index == self.correct_option_index