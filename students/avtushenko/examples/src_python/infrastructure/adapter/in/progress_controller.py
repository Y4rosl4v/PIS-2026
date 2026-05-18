from typing import Dict, Any
from application.port.in.submit_test_use_case import SubmitTestCommand, SubmitTestUseCase
from application.port.in.update_progress_use_case import UpdateProgressCommand, UpdateProgressUseCase

class ProgressController:
    """
    Входящий адаптер: REST API для управления прогрессом
    """
    
    def __init__(self, progress_service: UpdateProgressUseCase, test_service: SubmitTestUseCase):
        self.progress_service = progress_service
        self.test_service = test_service
    
    def update_lesson_progress(self, user_id: str, course_id: str, lesson_id: str, percent: float) -> Dict[str, Any]:
        """
        POST /api/courses/{course_id}/lessons/{lesson_id}/progress
        """
        # TODO:
        # 1. Создать UpdateProgressCommand
        # 2. Вызвать progress_service.execute(command)
        # 3. Вернуть JSON ответ
        # {
        #   "lesson_id": "...",
        #   "video_percent": 85.0,
        #   "is_completed": true,
        #   "next_lesson_unlocked": true
        # }
        raise NotImplementedError("Будет реализовано в Lab #4")
    
    def submit_test(self, user_id: str, course_id: str, answers: Dict[str, str]) -> Dict[str, Any]:
        """
        POST /api/courses/{course_id}/test/submit
        """
        # TODO:
        # 1. Создать SubmitTestCommand
        # 2. Вызвать test_service.execute(command)
        # 3. Вернуть JSON ответ
        # {
        #   "score": 85.0,
        #   "passed": true,
        #   "attempts": 1,
        #   "badge_id": "BADGE-123"
        # }
        raise NotImplementedError("Будет реализовано в Lab #4")