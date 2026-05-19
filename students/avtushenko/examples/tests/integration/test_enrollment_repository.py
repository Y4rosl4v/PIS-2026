import pytest
from app.infrastructure.adapter.out.enrollment_repository import EnrollmentRepository
from app.domain.aggregates import Enrollment

@pytest.mark.integration
class TestEnrollmentRepository:
    def test_save_and_find_enrollment(self, db_session):
        # Arrange
        repo = EnrollmentRepository(db_session)
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(5)
        
        # Act
        repo.save(enrollment)
        found = repo.find_by_id("E1")
        
        # Assert
        assert found is not None
        assert found.id == "E1"
        assert found.student_id == "S1"
        assert found.course_id == "C1"
        assert found._total_lessons == 5
    
    def test_update_enrollment_progress(self, db_session):
        # Arrange
        repo = EnrollmentRepository(db_session)
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(4)
        repo.save(enrollment)
        
        # Act - complete a lesson
        found = repo.find_by_id("E1")
        found.complete_lesson("L1")
        repo.save(found)
        
        # Assert
        updated = repo.find_by_id("E1")
        assert updated.progress.value == 25
        assert "L1" in updated._completed_lessons
    
    def test_find_by_student_and_course(self, db_session):
        # Arrange
        repo = EnrollmentRepository(db_session)
        enrollment = Enrollment("E1", "STU123", "CRS456")
        enrollment.set_total_lessons(3)
        repo.save(enrollment)
        
        # Act
        found = repo.find_by_student_and_course("STU123", "CRS456")
        
        # Assert
        assert found is not None
        assert found.id == "E1"
    
    def test_find_by_student_returns_all_enrollments(self, db_session):
        # Arrange
        repo = EnrollmentRepository(db_session)
        enrollment1 = Enrollment("E1", "STU123", "CRS1")
        enrollment2 = Enrollment("E2", "STU123", "CRS2")
        enrollment3 = Enrollment("E3", "OTHER", "CRS3")
        
        enrollment1.set_total_lessons(1)
        enrollment2.set_total_lessons(1)
        enrollment3.set_total_lessons(1)
        
        repo.save(enrollment1)
        repo.save(enrollment2)
        repo.save(enrollment3)
        
        # Act
        student_enrollments = repo.find_by_student("STU123")
        
        # Assert
        assert len(student_enrollments) == 2
        assert student_enrollments[0].student_id == "STU123"
        assert student_enrollments[1].student_id == "STU123"