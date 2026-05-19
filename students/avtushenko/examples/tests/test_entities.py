import pytest
from domain.entities import Course, Lesson
from domain.value_objects import VideoURL, TestQuestion

def test_course_equality():
    c1 = Course("C1", "Python", "Learn Python")
    c2 = Course("C1", "Python", "Learn Python")
    c3 = Course("C2", "Java", "Learn Java")
    assert c1 == c2
    assert c1 != c3

def test_course_add_lesson():
    course = Course("C1", "Title", "Desc")
    course.add_lesson("L1")
    assert "L1" in course.lesson_ids

def test_course_add_duplicate_lesson():
    course = Course("C1", "Title", "Desc")
    course.add_lesson("L1")
    with pytest.raises(ValueError):
        course.add_lesson("L1")

def test_lesson_attach_test():
    video = VideoURL("https://example.com/video.mp4")
    lesson = Lesson("L1", "Lesson 1", video)
    question = TestQuestion("Q?", ["A", "B"], 0)
    lesson.attach_test(question)
    assert lesson.test_question is not None