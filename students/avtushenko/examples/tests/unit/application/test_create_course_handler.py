import pytest
from unittest.mock import Mock
from app.application.command import CreateCourseCommand
from app.application.command.handlers import CreateCourseHandler

class TestCreateCourseHandler:
    def test_creates_course_successfully(self):
        # Arrange
        mock_repo = Mock()
        handler = CreateCourseHandler(mock_repo)
        command = CreateCourseCommand("Python Basics", "Learn Python")
        
        # Act
        course_id = handler.handle(command)
        
        # Assert
        assert course_id.startswith("COURSE-")
        mock_repo.save.assert_called_once()
        saved_course = mock_repo.save.call_args[0][0]
        assert saved_course.title == "Python Basics"
        assert saved_course.description == "Learn Python"
    
    def test_creates_course_with_unique_id(self):
        mock_repo = Mock()
        handler = CreateCourseHandler(mock_repo)
        
        id1 = handler.handle(CreateCourseCommand("Course 1", "Desc 1"))
        id2 = handler.handle(CreateCourseCommand("Course 2", "Desc 2"))
        
        assert id1 != id2
    
    def test_validation_fails_with_empty_title(self):
        mock_repo = Mock()
        handler = CreateCourseHandler(mock_repo)
        
        with pytest.raises(ValueError, match="cannot be empty"):
            handler.handle(CreateCourseCommand("", "Description"))
    
    def test_validation_fails_with_title_too_long(self):
        mock_repo = Mock()
        handler = CreateCourseHandler(mock_repo)
        long_title = "A" * 201
        
        with pytest.raises(ValueError, match="too long"):
            handler.handle(CreateCourseCommand(long_title, "Description"))