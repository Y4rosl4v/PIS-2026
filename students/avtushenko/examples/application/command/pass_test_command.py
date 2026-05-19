from dataclasses import dataclass

@dataclass(frozen=True)
class PassTestCommand:
    """Команда для прохождения теста"""
    enrollment_id: str
    lesson_id: str
    selected_option_index: int
    
    def __post_init__(self):
        if not self.enrollment_id or not self.enrollment_id.strip():
            raise ValueError("Enrollment ID cannot be empty")
        if not self.lesson_id or not self.lesson_id.strip():
            raise ValueError("Lesson ID cannot be empty")
        if self.selected_option_index < 0:
            raise ValueError("Selected option index must be >= 0")