from application.command import (
    CreateCourseCommand,
    EnrollStudentCommand,
    CompleteLessonCommand,
    PassTestCommand
)
from application.command.handlers import (
    CreateCourseHandler,
    EnrollStudentHandler,
    CompleteLessonHandler,
    PassTestHandler
)
from application.query import (
    GetCourseByIdQuery,
    ListCoursesQuery,
    GetStudentProgressQuery
)
from application.query.handlers import (
    GetCourseByIdHandler,
    ListCoursesHandler,
    GetStudentProgressHandler
)
from application.query.dto import CourseDTO, EnrollmentDTO
from typing import List

class CourseService:
    """
    Application Service Facade (Фасад)
    Делегирует выполнение команд и запросов соответствующим обработчикам
    """
    
    def __init__(self, repositories):
        """
        Args:
            repositories: dict с репозиториями
                - course_repository
                - enrollment_repository
                - lesson_repository
        """
        self._repositories = repositories
        
        # Инициализация обработчиков команд
        self._create_course_handler = CreateCourseHandler(
            repositories["course_repository"]
        )
        self._enroll_student_handler = EnrollStudentHandler(
            repositories["enrollment_repository"],
            repositories["course_repository"]
        )
        self._complete_lesson_handler = CompleteLessonHandler(
            repositories["enrollment_repository"]
        )
        self._pass_test_handler = PassTestHandler(
            repositories["enrollment_repository"],
            repositories["lesson_repository"]
        )
        
        # Инициализация обработчиков запросов
        self._get_course_by_id_handler = GetCourseByIdHandler(
            repositories["course_repository"]
        )
        self._list_courses_handler = ListCoursesHandler(
            repositories["course_repository"]
        )
        self._get_student_progress_handler = GetStudentProgressHandler(
            repositories["enrollment_repository"]
        )
    
    # ========== КОМАНДЫ (изменяют состояние) ==========
    
    def create_course(self, command: CreateCourseCommand) -> str:
        """Создать новый курс"""
        return self._create_course_handler.handle(command)
    
    def enroll_student(self, command: EnrollStudentCommand) -> str:
        """Записать студента на курс"""
        return self._enroll_student_handler.handle(command)
    
    def complete_lesson(self, command: CompleteLessonCommand) -> None:
        """Завершить урок"""
        self._complete_lesson_handler.handle(command)
    
    def pass_test(self, command: PassTestCommand) -> bool:
        """Пройти тест"""
        return self._pass_test_handler.handle(command)
    
    # ========== ЗАПРОСЫ (только чтение) ==========
    
    def get_course_by_id(self, query: GetCourseByIdQuery) -> CourseDTO:
        """Получить курс по ID"""
        return self._get_course_by_id_handler.handle(query)
    
    def list_courses(self, query: ListCoursesQuery) -> List[CourseDTO]:
        """Получить список курсов"""
        return self._list_courses_handler.handle(query)
    
    def get_student_progress(self, query: GetStudentProgressQuery) -> EnrollmentDTO:
        """Получить прогресс студента"""
        return self._get_student_progress_handler.handle(query)