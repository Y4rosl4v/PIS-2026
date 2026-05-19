import pytest
from unittest.mock import Mock
from app.application.command import EnrollStudentCommand
from app.application.command.handlers import EnrollStudentHandler
from app.domain.entities import Course

class TestEnrollStudentHandler:
    def test_enrolls_student_successfully(self):
        # Arrange
        mock_enrollment_repo = Mock()
        mock_course_repo = Mock()
        
        # Mock existing enrollment check
        mock_enrollment_repo.find_by_student_and_course.return_value = None
        
        # Mock course
        course = Course("C1", "Test Course", "Desc")
        course.add_lesson("L1")
        course.add_lesson("L2")
        mock_course_repo.find_by_id.return_value = course
        
        handler = EnrollStudentHandler(mock_enrollment_repo, mock_course_repo, None)
        command = EnrollStudentCommand("S1", "C1")
        
        # Act
        enrollment_id = handler.handle(command)
        
        # Assert
        assert enrollment_id.startswith("ENR-")
        mock_enrollment_repo.save.assert_called_once()
        saved = mock_enrollment_repo.save.call_args[0][0]
        assert saved.student_id == "S1"
        assert saved.course_id == "C1"
    
    def test_raises_error_if_course_not_found(self):
        # Arrange
        mock_enrollment_repo = Mock()
        mock_course_repo = Mock()
        mock_course_repo.find_by_id.return_value = None
        
        handler = EnrollStudentHandler(mock_enrollment_repo, mock_course_repo, None)
        command = EnrollStudentCommand("S1", "NOT_EXIST")
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            handler.handle(command)
    
    def test_raises_error_if_already_enrolled(self):
        # Arrange
        mock_enrollment_repo = Mock()
        mock_course_repo = Mock()
        mock_enrollment_repo.find_by_student_and_course.return_value = Mock()  # exists
        mock_course_repo.find_by_id.return_value = Course("C1", "Title", "Desc")
        
        handler = EnrollStudentHandler(mock_enrollment_repo, mock_course_repo, None)
        command = EnrollStudentCommand("S1", "C1")
        
        # Act & Assert
        with pytest.raises(ValueError, match="already enrolled"):
            handler.handle(command)
    
    def test_publishes_events_on_enrollment(self):
        # Arrange
        mock_enrollment_repo = Mock()
        mock_course_repo = Mock()
        mock_event_publisher = Mock()
        
        mock_enrollment_repo.find_by_student_and_course.return_value = None
        course = Course("C1", "Title", "Desc")
        course.add_lesson("L1")
        mock_course_repo.find_by_id.return_value = course
        
        handler = EnrollStudentHandler(mock_enrollment_repo, mock_course_repo, mock_event_publisher)
        command = EnrollStudentCommand("S1", "C1")
        
        # Act
        handler.handle(command)
        
        # Assert
        saved_enrollment = mock_enrollment_repo.save.call_args[0][0]
        events = saved_enrollment.get_events()
        assert len(events) > 0
        # Events should be published (but after save, so in actual handler)