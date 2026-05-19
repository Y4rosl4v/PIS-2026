import pytest
from app.domain.aggregates import Enrollment
from app.domain.events import EnrollmentStartedEvent, LessonCompletedEvent, CourseCompletedEvent

class TestEnrollment:
    def test_create_enrollment(self):
        enrollment = Enrollment("E1", "S1", "C1")
        assert enrollment.id == "E1"
        assert enrollment.student_id == "S1"
        assert enrollment.course_id == "C1"
    
    def test_set_total_lessons_and_register_event(self):
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(5)
        
        assert enrollment._total_lessons == 5
        events = enrollment.get_events()
        assert any(isinstance(e, EnrollmentStartedEvent) for e in events)
    
    def test_complete_lesson_updates_progress(self):
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(4)
        enrollment.complete_lesson("L1")
        
        assert enrollment.progress.value == 25
        events = enrollment.get_events()
        assert any(isinstance(e, LessonCompletedEvent) for e in events)
    
    def test_complete_lesson_twice_raises_error(self):
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(2)
        enrollment.complete_lesson("L1")
        
        with pytest.raises(ValueError, match="already completed"):
            enrollment.complete_lesson("L1")
    
    def test_complete_last_lesson_triggers_course_completed_event(self):
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(1)
        enrollment.complete_lesson("L1")
        
        events = enrollment.get_events()
        assert any(isinstance(e, CourseCompletedEvent) for e in events)
    
    def test_progress_calculation(self):
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(10)
        
        assert enrollment.progress.value == 0
        
        enrollment.complete_lesson("L1")
        enrollment.complete_lesson("L2")
        assert enrollment.progress.value == 20
        
        for i in range(3, 11):
            enrollment.complete_lesson(f"L{i}")
        assert enrollment.progress.value == 100
        assert enrollment.progress.is_completed() is True
    
    def test_pass_test_after_lesson(self):
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(2)
        enrollment.complete_lesson("L1")
        
        result = enrollment.pass_test("L1", 0, 0)
        assert result is True
    
    def test_pass_test_before_lesson_raises_error(self):
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(2)
        
        with pytest.raises(ValueError, match="Cannot take test"):
            enrollment.pass_test("L1", 0, 0)
    
    def test_events_are_cleared(self):
        enrollment = Enrollment("E1", "S1", "C1")
        enrollment.set_total_lessons(3)
        enrollment.complete_lesson("L1")
        
        assert len(enrollment.get_events()) > 0
        enrollment.clear_events()
        assert len(enrollment.get_events()) == 0