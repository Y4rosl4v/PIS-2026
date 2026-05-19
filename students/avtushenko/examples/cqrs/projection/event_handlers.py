from typing import Dict, Any
from app.domain.events import (
    EnrollmentStartedEvent,
    LessonCompletedEvent,
    CourseCompletedEvent
)
from app.cqrs.projection.course_projection import CourseProjection
from app.cqrs.projection.progress_projection import ProgressProjection

class EventHandlers:
    """
    Обработчики доменных событий для обновления read-моделей.
    Реализует eventual consistency через event-driven синхронизацию.
    """
    
    def __init__(self, db_session):
        self._db_session = db_session
        self._course_projection = CourseProjection(db_session)
        self._progress_projection = ProgressProjection(db_session)
    
    def handle(self, event) -> None:
        """Маршрутизация событий в соответствующие обработчики"""
        event_type = event.__class__.__name__
        
        handlers = {
            "EnrollmentStartedEvent": self._handle_enrollment_started,
            "LessonCompletedEvent": self._handle_lesson_completed,
            "CourseCompletedEvent": self._handle_course_completed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            handler(event)
    
    def _handle_enrollment_started(self, event: EnrollmentStartedEvent) -> None:
        """Обновление read-моделей при старте записи на курс"""
        # Обновляем проекцию прогресса студента
        self._progress_projection.on_enrollment_started(event)
        
        # Обновляем статистику курса
        self._course_projection.refresh_course_statistics(event.course_id)
    
    def _handle_lesson_completed(self, event: LessonCompletedEvent) -> None:
        """Обновление read-моделей при завершении урока"""
        # Обновляем проекцию прогресса
        self._progress_projection.on_lesson_completed(event)
        
        # Обновляем статистику курса
        self._course_projection.refresh_course_statistics_by_enrollment(event.enrollment_id)
    
    def _handle_course_completed(self, event: CourseCompletedEvent) -> None:
        """Обновление read-моделей при завершении курса"""
        # Обновляем проекцию прогресса
        self._progress_projection.on_course_completed(event)
        
        # Обновляем статистику курса
        self._course_projection.refresh_course_statistics(event.course_id)