import pytest
from app.domain.entities import Course
from app.domain.value_objects import Rating

class TestCourse:
    def test_create_course(self):
        course = Course("C1", "Python Basics", "Learn Python")
        assert course.id == "C1"
        assert course.title == "Python Basics"
        assert course.description == "Learn Python"
        assert course.rating is None
        assert course.lesson_ids == []
    
    def test_equality_by_id(self):
        course1 = Course("C1", "Title1", "Desc1")
        course2 = Course("C1", "Title2", "Desc2")  # Different title but same ID
        course3 = Course("C2", "Title1", "Desc1")
        
        assert course1 == course2
        assert course1 != course3
        assert hash(course1) == hash(course2)
    
    def test_add_lesson(self):
        course = Course("C1", "Title", "Desc")
        course.add_lesson("L1")
        assert "L1" in course.lesson_ids
    
    def test_add_duplicate_lesson_raises_error(self):
        course = Course("C1", "Title", "Desc")
        course.add_lesson("L1")
        with pytest.raises(ValueError, match="already in course"):
            course.add_lesson("L1")
    
    def test_update_rating(self):
        course = Course("C1", "Title", "Desc")
        rating = Rating(4.5)
        course.update_rating(rating)
        assert course.rating == rating
    
    def test_lesson_ids_returns_copy(self):
        course = Course("C1", "Title", "Desc")
        course.add_lesson("L1")
        lesson_ids = course.lesson_ids
        lesson_ids.append("L2")
        assert "L2" not in course.lesson_ids  # Original unchanged