import pytest
from app.cqrs.read_model import CourseReadModel, EnrollmentReadModel
from app.cqrs.read_model.repositories import CourseReadRepository, ProgressReadRepository

@pytest.mark.unit
class TestCourseReadRepository:
    
    def test_find_by_id_returns_denormalized_data(self, mock_db_session):
        # Arrange
        repo = CourseReadRepository(mock_db_session)
        
        # Act
        course = repo.find_by_id("C1")
        
        # Assert
        assert course is not None
        assert isinstance(course, CourseReadModel)
        assert course.total_students >= 0
        assert course.average_progress >= 0
    
    def test_find_all_summaries_returns_list(self, mock_db_session):
        repo = CourseReadRepository(mock_db_session)
        
        courses = repo.find_all_summaries(limit=10)
        
        assert isinstance(courses, list)
        for c in courses:
            assert hasattr(c, 'total_students')
    
    def test_find_top_rated_returns_sorted(self, mock_db_session):
        repo = CourseReadRepository(mock_db_session)
        
        top = repo.find_top_rated(limit=5)
        
        # Проверяем сортировку по убыванию рейтинга
        ratings = [c.rating for c in top if c.rating]
        if len(ratings) > 1:
            assert ratings == sorted(ratings, reverse=True)
    
    def test_find_most_popular_returns_sorted(self, mock_db_session):
        repo = CourseReadRepository(mock_db_session)
        
        popular = repo.find_most_popular(limit=5)
        
        # Проверяем сортировку по убыванию количества студентов
        counts = [c.total_students for c in popular]
        if len(counts) > 1:
            assert counts == sorted(counts, reverse=True)

@pytest.mark.unit
class TestProgressReadRepository:
    
    def test_find_by_student_and_course(self, mock_db_session):
        repo = ProgressReadRepository(mock_db_session)
        
        progress = repo.find_by_student_and_course("STU001", "C1")
        
        if progress:
            assert isinstance(progress, EnrollmentReadModel)
            assert progress.progress_percent >= 0
            assert progress.progress_percent <= 100
    
    def test_find_by_student_aggregates_progress(self, mock_db_session):
        repo = ProgressReadRepository(mock_db_session)
        
        student_progress = repo.find_by_student("STU001")
        
        assert student_progress.total_courses >= 0
        assert student_progress.completed_courses <= student_progress.total_courses
        assert 0 <= student_progress.average_progress <= 100
    
    def test_find_all_active_students(self, mock_db_session):
        repo = ProgressReadRepository(mock_db_session)
        
        active = repo.find_all_active_students(min_progress=50)
        
        for student in active:
            assert student["avg_progress"] >= 50