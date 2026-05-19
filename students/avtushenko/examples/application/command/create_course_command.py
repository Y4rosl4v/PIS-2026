from dataclasses import dataclass

@dataclass(frozen=True)
class CreateCourseCommand:
    """Команда для создания нового курса"""
    title: str
    description: str
    
    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Course title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Course title too long (max 200 chars)")
        if not self.description:
            raise ValueError("Course description cannot be empty")