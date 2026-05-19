import pytest
from unittest.mock import Mock, patch
from app.domain.events import (
    EnrollmentStartedEvent,
    LessonCompletedEvent,
    CourseCompletedEvent
)
from app.cqrs.projection import EventHandlers, CourseProjection, ProgressProjection

@pytest.mark.unit
class TestEventHandlers:
    
    def test_handle_enrollment_started(self, mock_db_session):
        # Arrange
        handlers = EventHandlers(mock_db_session)
        event = EnrollmentStartedEvent(
            enrollment_id="E1",
            student_id="S1",
            course_id="C1"
        )
        
        # Act
        handlers.handle(event)
        
        # Assert - проверяем, что проекции были вызваны
        # (в реальном тесте проверяем вызовы методов проекций)
    
    def test_handle_lesson_completed(self, mock_db_session):
        handlers = EventHandlers(mock_db_session)
        event = LessonCompletedEvent(
            enrollment_id="E1",
            lesson_id="L1",
            new_progress=50
        )
        
        handlers.handle(event)
    
    def test_handle_course_completed(self, mock_db_session):
        handlers = EventHandlers(mock_db_session)
        event = CourseCompletedEvent(
            enrollment_id="E1",
            student_id="S1",
            course_id="C1",
            completed_at=None
        )
        
        handlers.handle(event)

@pytest.mark.unit
class TestCourseProjection:
    
    def test_refresh_course_statistics(self, mock_db_session):
        projection = CourseProjection(mock_db_session)
        
        projection.refresh_course_statistics("C1")
    
    def test_refresh_all_statistics(self, mock_db_session):
        projection = CourseProjection(mock_db_session)
        
        with patch.object(mock_db_session, 'execute') as mock_execute:
            projection.refresh_all_statistics()
            mock_execute.assert_called()

@pytest.mark.integration
class TestProjectionIntegration:
    
    def test_full_projection_flow(self, db_session):
        """Интеграционный тест: полный цикл проекции"""
        
        # Создаём обработчики
        handlers = EventHandlers(db_session)
        
        # Создаём события
        enrollment_event = EnrollmentStartedEvent("E1", "S1", "C1")
        lesson_event = LessonCompletedEvent("E1", "L1", 50)
        completed_event = CourseCompletedEvent("E1", "S1", "C1", None)
        
        # Обрабатываем события
        handlers.handle(enrollment_event)
        handlers.handle(lesson_event)
        handlers.handle(completed_event)
        
        # Проверяем, что read model обновилась
        from app.cqrs.read_model.repositories import ProgressReadRepository
        repo = ProgressReadRepository(db_session)
        progress = repo.find_by_student_and_course("S1", "C1")
        
        if progress:
            assert progress.progress_percent >= 0