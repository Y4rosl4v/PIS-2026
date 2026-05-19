import pytest
from app.domain.entities import Lesson
from app.domain.value_objects import VideoURL, TestQuestion

class TestLesson:
    def test_create_lesson(self):
        video = VideoURL("https://example.com/video.mp4")
        lesson = Lesson("L1", "Introduction", video)
        assert lesson.id == "L1"
        assert lesson.title == "Introduction"
        assert lesson.video_url == video
        assert lesson.test_question is None
    
    def test_attach_test(self):
        video = VideoURL("https://example.com/video.mp4")
        lesson = Lesson("L1", "Title", video)
        question = TestQuestion("Q?", ["A", "B"], 0)
        lesson.attach_test(question)
        assert lesson.test_question == question
    
    def test_equality_by_id(self):
        video1 = VideoURL("https://example.com/v1.mp4")
        video2 = VideoURL("https://example.com/v2.mp4")
        lesson1 = Lesson("L1", "Title1", video1)
        lesson2 = Lesson("L1", "Title2", video2)  # Different content, same ID
        lesson3 = Lesson("L2", "Title1", video1)
        
        assert lesson1 == lesson2
        assert lesson1 != lesson3