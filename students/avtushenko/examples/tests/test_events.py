from domain.aggregates import Enrollment
from domain.events import LessonCompletedEvent, CourseCompletedEvent

def test_lesson_completed_event_registered():
    enrollment = Enrollment("E1", "S1", "C1")
    enrollment.set_total_lessons(2)
    enrollment.complete_lesson("L1")
    events = enrollment.get_events()
    assert any(isinstance(e, LessonCompletedEvent) for e in events)

def test_course_completed_event_registered():
    enrollment = Enrollment("E1", "S1", "C1")
    enrollment.set_total_lessons(1)
    enrollment.complete_lesson("L1")
    events = enrollment.get_events()
    assert any(isinstance(e, CourseCompletedEvent) for e in events)

def test_multiple_events():
    enrollment = Enrollment("E1", "S1", "C1")
    enrollment.set_total_lessons(2)
    enrollment.complete_lesson("L1")
    enrollment.complete_lesson("L2")
    events = enrollment.get_events()
    completed_events = [e for e in events if isinstance(e, LessonCompletedEvent)]
    assert len(completed_events) == 2