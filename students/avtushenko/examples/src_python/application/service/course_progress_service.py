from typing import Dict
from application.port.in.submit_test_use_case import SubmitTestUseCase, SubmitTestCommand, SubmitTestResult
from application.port.in.update_progress_use_case import UpdateProgressUseCase, UpdateProgressCommand, UpdateProgressResult
from application.port.out.progress_repository import ProgressRepository
from application.port.out.notification_service import NotificationService
from domain.models.progress import CourseProgress, LessonProgress, ProgressStatus
from domain.exceptions.domain_exception import (
    MaxAttemptsReachedException,
    LessonNotUnlockedException,
    InvalidProgressException
)

class CourseProgressService(SubmitTestUseCase, UpdateProgressUseCase):
    """
    Application Service: Управление прогрессом обучения
    Реализует use-cases для прохождения курсов
    """
    
    def __init__(self, progress_repo: ProgressRepository, notifier: NotificationService):
        self.progress_repo = progress_repo
        self.notifier = notifier
    
    def execute(self, command: UpdateProgressCommand) -> UpdateProgressResult:
        """Обновить прогресс просмотра урока"""
        # TODO: 
        # 1. Найти или создать прогресс курса
        # 2. Проверить, разблокирован ли урок
        # 3. Обновить прогресс урока
        # 4. Сохранить через repository
        # 5. Проверить, разблокирован ли следующий урок
        # 6. Вернуть результат
        raise NotImplementedError("Будет реализовано в Lab #4")
    
    def submit_test(self, command: SubmitTestCommand) -> SubmitTestResult:
        """Сдать итоговый тест"""
        # TODO:
        # 1. Найти прогресс курса
        # 2. Проверить, что все уроки просмотрены на 100%
        # 3. Проверить attempts < max_attempts
        # 4. Подсчитать балл (вызвать Test.calculate_score)
        # 5. Обновить прогресс (complete)
        # 6. Если passed=True -> создать badge, отправить уведомление
        # 7. Вернуть результат
        raise NotImplementedError("Будет реализовано в Lab #4")