from typing import Optional
from domain.value_objects import VideoURL, TestQuestion

class Lesson:
    """Entity: Урок (внутри курса)"""

    def __init__(self, lesson_id: str, title: str, video_url: VideoURL):
        self._id = lesson_id
        self._title = title
        self._video_url = video_url
        self._test_question: Optional[TestQuestion] = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def video_url(self) -> VideoURL:
        return self._video_url

    @property
    def test_question(self) -> Optional[TestQuestion]:
        return self._test_question

    def attach_test(self, question: TestQuestion) -> None:
        """Прикрепить тест к уроку"""
        self._test_question = question

    def __eq__(self, other) -> bool:
        if not isinstance(other, Lesson):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)