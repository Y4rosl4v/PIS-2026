from dataclasses import dataclass

@dataclass(frozen=True)
class EnrollStudentCommand:
    """Команда для записи студента на курс"""
    student_id: str
    course_id: str
    
    def __post_init__(self):
        if not self.student_id or not self.student_id.strip():
            raise ValueError("Student ID cannot be empty")
        if not self.course_id or not self.course_id.strip():
            raise ValueError("Course ID cannot be empty")