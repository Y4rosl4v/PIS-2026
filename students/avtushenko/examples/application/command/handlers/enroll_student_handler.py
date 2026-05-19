from domain.aggregates import Enrollment
from domain.events import EnrollmentStartedEvent
from application.command import EnrollStudentCommand

class EnrollStudentHandler:
    """Обработчик команды записи студента на курс"""
    
    def __init__(self, enrollment_repository, course_repository):
        self._enrollment_repository = enrollment_repository
        self._course_repository = course_repository
    
    def handle(self, command: EnrollStudentCommand) -> str:
        """Записать студента на курс и вернуть ID записи"""
        # 1. Проверка существования курса
        course = self._course_repository.find_by_id(command.course_id)
        if not course:
            raise ValueError(f"Course {command.course_id} not found")
        
        # 2. Проверка, не записан ли уже студент
        existing = self._enrollment_repository.find_by_student_and_course(
            command.student_id, command.course_id
        )
        if existing:
            raise ValueError(f"Student already enrolled in course {command.course_id}")
        
        # 3. Создание агрегата Enrollment
        enrollment_id = self._generate_enrollment_id()
        enrollment = Enrollment(
            enrollment_id, 
            command.student_id, 
            command.course_id
        )
        
        # 4. Установка общего количества уроков
        total_lessons = len(course.lesson_ids)
        enrollment.set_total_lessons(total_lessons)
        
        # 5. Сохранение
        self._enrollment_repository.save(enrollment)
        
        # 6. Публикация событий (в реальном проекте - через event bus)
        for event in enrollment.get_events():
            self._publish_event(event)
        enrollment.clear_events()
        
        return enrollment_id
    
    def _generate_enrollment_id(self) -> str:
        import uuid
        return f"ENR-{uuid.uuid4().hex[:8].upper()}"
    
    def _publish_event(self, event):
        # В реальном проекте здесь была бы публикация в Event Bus
        print(f"Event published: {event}")