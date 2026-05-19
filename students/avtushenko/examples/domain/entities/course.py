from typing import List, Optional
from domain.value_objects import Rating

class Course:
    """Entity: Курс (имеет уникальный ID)"""

    def __init__(self, course_id: str, title: str, description: str):
        self._id = course_id
        self._title = title
        self._description = description
        self._rating: Optional[Rating] = None
        self._lessons: List[str] = []  # IDs уроков

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def rating(self) -> Optional[Rating]:
        return self._rating

    @property
    def lesson_ids(self) -> List[str]:
        return self._lessons.copy()

    def add_lesson(self, lesson_id: str) -> None:
        """Добавить урок в курс"""
        if lesson_id in self._lessons:
            raise ValueError(f"Lesson {lesson_id} already in course")
        self._lessons.append(lesson_id)

    def update_rating(self, new_rating: Rating) -> None:
        """Обновить рейтинг курса"""
        self._rating = new_rating

    def __eq__(self, other) -> bool:
        if not isinstance(other, Course):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)