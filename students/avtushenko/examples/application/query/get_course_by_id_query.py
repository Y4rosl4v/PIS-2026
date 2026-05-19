from dataclasses import dataclass

@dataclass(frozen=True)
class GetCourseByIdQuery:
    """Запрос для получения курса по ID"""
    course_id: str
    
    def __post_init__(self):
        if not self.course_id or not self.course_id.strip():
            raise ValueError("Course ID cannot be empty")