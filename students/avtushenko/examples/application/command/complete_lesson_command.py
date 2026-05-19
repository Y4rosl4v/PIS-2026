from dataclasses import dataclass

@dataclass(frozen=True)
class CompleteLessonCommand:
    """Команда для завершения урока"""
    enrollment_id: str
    lesson_id: str
    
    def __post_init__(self):
        if not self.enrollment_id or not self.enrollment_id.strip():
            raise ValueError("Enrollment ID cannot be empty")
        if not self.lesson_id or not self.lesson_id.strip():
            raise ValueError("Lesson ID cannot be empty")