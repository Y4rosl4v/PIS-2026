from datetime import datetime
from typing import List, Optional, Dict
from domain.value_objects import ProgressPercent
from domain.events import (
    EnrollmentStartedEvent,
    LessonCompletedEvent,
    TestPassedEvent,
    CourseCompletedEvent
)

class Enrollment:
    """
    Aggregate Root: Запись студента на курс.
    Инкапсулирует прогресс, завершённые уроки, результаты тестов.
    """

    def __init__(self, enrollment_id: str, student_id: str, course_id: str):
        self._id = enrollment_id
        self._student_id = student_id
        self._course_id = course_id
        self._started_at = datetime.now()
        self._completed_lessons: List[str] = []  # IDs завершённых уроков
        self._test_results: Dict[str, bool] = {}  # lesson_id -> passed
        self._events: List = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def course_id(self) -> str:
        return self._course_id

    @property
    def progress(self) -> ProgressPercent:
        """Прогресс вычисляется на основе завершённых уроков"""
        if not self._total_lessons:
            return ProgressPercent(0)
        percent = int((len(self._completed_lessons) / self._total_lessons) * 100)
        return ProgressPercent(percent)

    def set_total_lessons(self, total: int) -> None:
        """Установить общее количество уроков в курсе"""
        self._total_lessons = total
        self._register_event(EnrollmentStartedEvent(
            enrollment_id=self._id,
            student_id=self._student_id,
            course_id=self._course_id
        ))

    # Инвариант #1: Нельзя завершить урок дважды
    def complete_lesson(self, lesson_id: str) -> None:
        """Завершить урок"""
        if lesson_id in self._completed_lessons:
            raise ValueError(f"Lesson {lesson_id} already completed")

        self._completed_lessons.append(lesson_id)
        self._register_event(LessonCompletedEvent(
            enrollment_id=self._id,
            lesson_id=lesson_id,
            new_progress=self.progress.value
        ))

        # Инвариант #2: Если курс завершён — генерируем событие
        if self.progress.value == 100:
            self._register_event(CourseCompletedEvent(
                enrollment_id=self._id,
                student_id=self._student_id,
                course_id=self._course_id,
                completed_at=datetime.now()
            ))

    # Инвариант #3: Тест можно пройти только после завершения урока
    def pass_test(self, lesson_id: str, selected_index: int, correct_index: int) -> bool:
        """Пройти тест к уроку"""
        if lesson_id not in self._completed_lessons:
            raise ValueError(f"Cannot take test for lesson {lesson_id} before completing it")

        passed = (selected_index == correct_index)

        if lesson_id not in self._test_results:
            self._test_results[lesson_id] = passed
            self._register_event(TestPassedEvent(
                enrollment_id=self._id,
                lesson_id=lesson_id,
                passed=passed
            ))

        return passed

    def _register_event(self, event) -> None:
        self._events.append(event)

    def get_events(self) -> List:
        return self._events.copy()

    def clear_events(self) -> None:
        self._events.clear()

    # Для вычисления прогресса
    _total_lessons: int = 0