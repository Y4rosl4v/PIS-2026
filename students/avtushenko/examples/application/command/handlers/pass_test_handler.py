from domain.entities import Lesson
from application.command import PassTestCommand

class PassTestHandler:
    """Обработчик команды прохождения теста"""
    
    def __init__(self, enrollment_repository, lesson_repository):
        self._enrollment_repository = enrollment_repository
        self._lesson_repository = lesson_repository
    
    def handle(self, command: PassTestCommand) -> bool:
        """Пройти тест и вернуть результат"""
        # 1. Загрузка агрегата
        enrollment = self._enrollment_repository.find_by_id(command.enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {command.enrollment_id} not found")
        
        # 2. Загрузка урока для получения правильного ответа
        lesson = self._lesson_repository.find_by_id(command.lesson_id)
        if not lesson or not lesson.test_question:
            raise ValueError(f"Lesson {command.lesson_id} has no test")
        
        # 3. Проверка ответа через доменную логику
        correct_index = lesson.test_question.correct_option_index
        passed = enrollment.pass_test(
            command.lesson_id,
            command.selected_option_index,
            correct_index
        )
        
        # 4. Сохранение изменений
        self._enrollment_repository.save(enrollment)
        
        # 5. Публикация событий
        for event in enrollment.get_events():
            self._publish_event(event)
        enrollment.clear_events()
        
        return passed
    
    def _publish_event(self, event):
        print(f"Event published: {event}")