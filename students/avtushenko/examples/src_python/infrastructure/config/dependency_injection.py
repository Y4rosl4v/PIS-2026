from application.service.course_progress_service import CourseProgressService
from infrastructure.adapter.out.in_memory_progress_repository import InMemoryProgressRepository
from infrastructure.adapter.out.console_notification_service import ConsoleNotificationService

class DependencyContainer:
    """
    Конфигурация DI: связывание портов и адаптеров
    """
    
    def __init__(self):
        # Создаём исходящие адаптеры
        self.progress_repository = InMemoryProgressRepository()
        self.notification_service = ConsoleNotificationService()
        
        # Создаём application service с инжекцией зависимостей
        self.course_progress_service = CourseProgressService(
            progress_repo=self.progress_repository,
            notifier=self.notification_service
        )
    
    def get_progress_service(self):
        """Получить сервис для обновления прогресса"""
        return self.course_progress_service
    
    def get_test_service(self):
        """Получить сервис для сдачи теста"""
        return self.course_progress_service