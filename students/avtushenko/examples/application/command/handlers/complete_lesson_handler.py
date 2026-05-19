from application.command import CompleteLessonCommand

class CompleteLessonHandler:
    """Обработчик команды завершения урока"""
    
    def __init__(self, enrollment_repository):
        self._enrollment_repository = enrollment_repository
    
    def handle(self, command: CompleteLessonCommand) -> None:
        """Завершить урок"""
        # 1. Загрузка агрегата
        enrollment = self._enrollment_repository.find_by_id(command.enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {command.enrollment_id} not found")
        
        # 2. Вызов метода агрегата (с инвариантами)
        enrollment.complete_lesson(command.lesson_id)
        
        # 3. Сохранение изменений
        self._enrollment_repository.save(enrollment)
        
        # 4. Публикация событий
        for event in enrollment.get_events():
            self._publish_event(event)
        enrollment.clear_events()
    
    def _publish_event(self, event):
        print(f"Event published: {event}")