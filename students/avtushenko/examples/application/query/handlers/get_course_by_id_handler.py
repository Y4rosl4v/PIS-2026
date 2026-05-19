from application.query import GetCourseByIdQuery
from application.query.dto import CourseDTO

class GetCourseByIdHandler:
    """Обработчик запроса получения курса по ID"""
    
    def __init__(self, course_repository):
        self._course_repository = course_repository
    
    def handle(self, query: GetCourseByIdQuery) -> CourseDTO:
        """Получить курс и преобразовать в DTO"""
        course = self._course_repository.find_by_id(query.course_id)
        if not course:
            raise ValueError(f"Course {query.course_id} not found")
        
        return CourseDTO(
            id=course.id,
            title=course.title,
            description=course.description,
            rating=course.rating.value if course.rating else None,
            lesson_ids=course.lesson_ids,
            total_lessons=len(course.lesson_ids)
        )