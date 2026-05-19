from domain.entities import Course
from application.command import CreateCourseCommand

class CreateCourseHandler:
    """Обработчик команды создания курса"""
    
    def __init__(self, course_repository):
        self._course_repository = course_repository
    
    def handle(self, command: CreateCourseCommand) -> str:
        """Создать курс и вернуть его ID"""
        # 1. Валидация (уже в команде)
        # 2. Создание агрегата
        course_id = self._generate_course_id()
        course = Course(course_id, command.title, command.description)
        
        # 3. Сохранение через репозиторий
        self._course_repository.save(course)
        
        # 4. Возврат ID
        return course_id
    
    def _generate_course_id(self) -> str:
        import uuid
        return f"COURSE-{uuid.uuid4().hex[:8].upper()}"