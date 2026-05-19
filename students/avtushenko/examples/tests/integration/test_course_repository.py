import pytest
from app.infrastructure.adapter.out.course_repository import CourseRepository
from app.domain.entities import Course
from app.domain.value_objects import Rating

@pytest.mark.integration
class TestCourseRepository:
    def test_save_and_find_course(self, db_session):
        # Arrange
        repo = CourseRepository(db_session)
        course = Course("C1", "Python Basics", "Learn Python")
        
        # Act
        repo.save(course)
        found = repo.find_by_id("C1")
        
        # Assert
        assert found is not None
        assert found.id == "C1"
        assert found.title == "Python Basics"
        assert found.description == "Learn Python"
    
    def test_update_course(self, db_session):
        # Arrange
        repo = CourseRepository(db_session)
        course = Course("C1", "Original Title", "Original Desc")
        repo.save(course)
        
        # Act - update
        updated_course = Course("C1", "New Title", "New Desc")
        updated_course.update_rating(Rating(4.5))
        repo.save(updated_course)
        
        # Assert
        found = repo.find_by_id("C1")
        assert found.title == "New Title"
        assert found.description == "New Desc"
        assert found.rating.value == 4.5
    
    def test_find_all_courses(self, db_session):
        # Arrange
        repo = CourseRepository(db_session)
        course1 = Course("C1", "Course 1", "Desc 1")
        course2 = Course("C2", "Course 2", "Desc 2")
        repo.save(course1)
        repo.save(course2)
        
        # Act
        all_courses = repo.find_all()
        
        # Assert
        assert len(all_courses) >= 2
        titles = [c.title for c in all_courses]
        assert "Course 1" in titles
        assert "Course 2" in titles
    
    def test_find_all_with_pagination(self, db_session):
        # Arrange
        repo = CourseRepository(db_session)
        for i in range(10):
            course = Course(f"C{i}", f"Course {i}", f"Desc {i}")
            repo.save(course)
        
        # Act
        first_page = repo.find_all(limit=5, offset=0)
        second_page = repo.find_all(limit=5, offset=5)
        
        # Assert
        assert len(first_page) == 5
        assert len(second_page) == 5
    
    def test_delete_course(self, db_session):
        # Arrange
        repo = CourseRepository(db_session)
        course = Course("C1", "To Delete", "Desc")
        repo.save(course)
        assert repo.find_by_id("C1") is not None
        
        # Act
        result = repo.delete("C1")
        
        # Assert
        assert result is True
        assert repo.find_by_id("C1") is None
    
    def test_find_nonexistent_returns_none(self, db_session):
        repo = CourseRepository(db_session)
        found = repo.find_by_id("NOT_EXIST")
        assert found is None