import pytest
from unittest.mock import Mock
from app.application.command import CompleteLessonCommand
from app.application.command.handlers import CompleteLessonHandler
from app.domain.aggregates import Enrollment

class TestCompleteLessonHandler:
    def test_completes_lesson_successfully(self):
        # Arrange
        mock_repo = Mock()
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(3)
        mock_repo.find_by_id.return_value = enrollment
        
        handler = CompleteLessonHandler(mock_repo, None)
        command = CompleteLessonCommand("E1", "L1")
        
        # Act
        handler.handle(command)
        
        # Assert
        mock_repo.save.assert_called_once()
        saved = mock_repo.save.call_args[0][0]
        assert saved.progress.value == 33
    
    def test_raises_error_if_enrollment_not_found(self):
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None
        
        handler = CompleteLessonHandler(mock_repo, None)
        command = CompleteLessonCommand("NOT_EXIST", "L1")
        
        with pytest.raises(ValueError, match="not found"):
            handler.handle(command)
    
    def test_raises_error_if_lesson_already_completed(self):
        mock_repo = Mock()
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(2)
        enrollment.complete_lesson("L1")  # First completion
        mock_repo.find_by_id.return_value = enrollment
        
        handler = CompleteLessonHandler(mock_repo, None)
        command = CompleteLessonCommand("E1", "L1")
        
        with pytest.raises(ValueError, match="already completed"):
            handler.handle(command)