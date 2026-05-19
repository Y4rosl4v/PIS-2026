import pytest
from domain.aggregates import Enrollment
from domain.exceptions import LessonAlreadyCompletedError

def test_enrollment_complete_lesson():
    enrollment = Enrollment("E1", "S1", "C1")
    enrollment.set_total_lessons(3)
    enrollment.complete_lesson("L1")
    assert enrollment.progress.value == 33

def test_enrollment_cannot_complete_twice():
    enrollment = Enrollment("E1", "S1", "C1")
    enrollment.set_total_lessons(3)
    enrollment.complete_lesson("L1")
    with pytest.raises(ValueError, match="already completed"):
        enrollment.complete_lesson("L1")

def test_enrollment_course_completion_event():
    enrollment = Enrollment("E1", "S1", "C1")
    enrollment.set_total_lessons(1)
    enrollment.complete_lesson("L1")
    events = enrollment.get_events()
    assert any("CourseCompletedEvent" in str(type(e)) for e in events)

def test_enrollment_test_before_lesson():
    enrollment = Enrollment("E1", "S1", "C1")
    enrollment.set_total_lessons(2)
    with pytest.raises(ValueError, match="Cannot take test"):
        enrollment.pass_test("L1", 0, 0)

def test_enrollment_test_after_lesson():
    enrollment = Enrollment("E1", "S1", "C1")
    enrollment.set_total_lessons(2)
    enrollment.complete_lesson("L1")
    result = enrollment.pass_test("L1", 1, 1)
    assert result == True