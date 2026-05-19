import pytest
from unittest.mock import Mock, MagicMock
from domain.aggregates import Enrollment
from domain.entities import Course, Lesson
from domain.value_objects import VideoURL, TestQuestion
from application.command import (
    CreateCourseCommand,
    EnrollStudentCommand,
    CompleteLessonCommand,
    PassTestCommand
)
from application.command.handlers import (
    CreateCourseHandler,
    EnrollStudentHandler,
    CompleteLessonHandler,
    PassTestHandler
)

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

class TestEnrollStudentHandler:
    def test_enrolls_student_successfully(self):
        # Arrange
        mock_course_repo = Mock()
        mock_enrollment_repo = Mock()
        mock_enrollment_repo.find_by_student_and_course.return_value = None
        
        course = Course("C1", "Test Course", "Desc")
        course.add_lesson("L1")
        course.add_lesson("L2")
        mock_course_repo.find_by_id.return_value = course
        
        handler = EnrollStudentHandler(mock_enrollment_repo, mock_course_repo)
        command = EnrollStudentCommand("S1", "C1")
        
        # Act
        enrollment_id = handler.handle(command)
        
        # Assert
        assert enrollment_id.startswith("ENR-")
        mock_enrollment_repo.save.assert_called_once()
    
    def test_raises_error_if_already_enrolled(self):
        # Arrange
        mock_course_repo = Mock()
        mock_enrollment_repo = Mock()
        mock_enrollment_repo.find_by_student_and_course.return_value = Mock()
        
        handler = EnrollStudentHandler(mock_enrollment_repo, mock_course_repo)
        command = EnrollStudentCommand("S1", "C1")
        
        # Act & Assert
        with pytest.raises(ValueError, match="already enrolled"):
            handler.handle(command)

class TestCompleteLessonHandler:
    def test_completes_lesson_successfully(self):
        # Arrange
        mock_repo = Mock()
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(2)
        mock_repo.find_by_id.return_value = enrollment
        
        handler = CompleteLessonHandler(mock_repo)
        command = CompleteLessonCommand("E1", "L1")
        
        # Act
        handler.handle(command)
        
        # Assert
        mock_repo.save.assert_called_once()
        saved_enrollment = mock_repo.save.call_args[0][0]
        assert saved_enrollment.progress.value == 50

class TestPassTestHandler:
    def test_passes_test_correctly(self):
        # Arrange
        mock_enrollment_repo = Mock()
        mock_lesson_repo = Mock()
        
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(2)
        enrollment.complete_lesson("L1")  # Завершаем урок
        mock_enrollment_repo.find_by_id.return_value = enrollment
        
        video = VideoURL("https://example.com/video.mp4")
        question = TestQuestion("Q?", ["A", "B"], 0)
        lesson = Lesson("L1", "Lesson 1", video)
        lesson.attach_test(question)
        mock_lesson_repo.find_by_id.return_value = lesson
        
        handler = PassTestHandler(mock_enrollment_repo, mock_lesson_repo)
        command = PassTestCommand("E1", "L1", 0)
        
        # Act
        result = handler.handle(command)
        
        # Assert
        assert result == True
        mock_enrollment_repo.save.assert_called_once()