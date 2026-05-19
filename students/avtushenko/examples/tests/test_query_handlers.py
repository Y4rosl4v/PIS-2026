import pytest
from unittest.mock import Mock
from domain.entities import Course
from domain.value_objects import Rating
from application.query import (
    GetCourseByIdQuery,
    ListCoursesQuery,
    GetStudentProgressQuery
)
from application.query.handlers import (
    GetCourseByIdHandler,
    ListCoursesHandler,
    GetStudentProgressHandler
)
from application.query.dto import CourseDTO

class TestGetCourseByIdHandler:
    def test_returns_course_dto_when_found(self):
        # Arrange
        mock_repo = Mock()
        course = Course("C1", "Python", "Learn Python")
        course.update_rating(Rating(4.5))
        mock_repo.find_by_id.return_value = course
        
        handler = GetCourseByIdHandler(mock_repo)
        query = GetCourseByIdQuery("C1")
        
        # Act
        result = handler.handle(query)
        
        # Assert
        assert isinstance(result, CourseDTO)
        assert result.id == "C1"
        assert result.title == "Python"
        assert result.rating == 4.5
    
    def test_raises_error_when_not_found(self):
        # Arrange
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None
        
        handler = GetCourseByIdHandler(mock_repo)
        query = GetCourseByIdQuery("NOT_EXIST")
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            handler.handle(query)

class TestListCoursesHandler:
    def test_returns_list_of_courses(self):
        # Arrange
        mock_repo = Mock()
        course1 = Course("C1", "Python", "Desc1")
        course2 = Course("C2", "Java", "Desc2")
        mock_repo.find_all.return_value = [course1, course2]
        
        handler = ListCoursesHandler(mock_repo)
        query = ListCoursesQuery(limit=10, offset=0)
        
        # Act
        results = handler.handle(query)
        
        # Assert
        assert len(results) == 2
        assert all(isinstance(r, CourseDTO) for r in results)

class TestGetStudentProgressHandler:
    def test_returns_progress_dto(self):
        # Arrange
        mock_repo = Mock()
        enrollment = Mock()
        enrollment.id = "E1"
        enrollment.student_id = "S1"
        enrollment.course_id = "C1"
        enrollment.progress.value = 75
        enrollment.progress.is_completed.return_value = False
        enrollment._completed_lessons = ["L1", "L2"]
        mock_repo.find_by_student_and_course.return_value = enrollment
        
        handler = GetStudentProgressHandler(mock_repo)
        query = GetStudentProgressQuery("S1", "C1")
        
        # Act
        result = handler.handle(query)
        
        # Assert
        assert result.student_id == "S1"
        assert result.progress_percent == 75
        assert result.is_completed == False