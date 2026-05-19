from typing import List
from application.query import ListCoursesQuery
from application.query.dto import CourseDTO

class ListCoursesHandler:
    """Обработчик запроса списка курсов"""
    
    def __init__(self, course_repository):
        self._course_repository = course_repository
    
    def handle(self, query: ListCoursesQuery) -> List[CourseDTO]:
        """Получить список курсов с фильтрацией и пагинацией"""
        courses = self._course_repository.find_all()
        
        # Применяем фильтры
        if query.min_rating is not None:
            courses = [c for c in courses 
                      if c.rating and c.rating.value >= query.min_rating]
        
        # Пагинация
        courses = courses[query.offset:query.offset + query.limit]
        
        # Преобразование в DTO
        return [
            CourseDTO(
                id=c.id,
                title=c.title,
                description=c.description,
                rating=c.rating.value if c.rating else None,
                lesson_ids=c.lesson_ids,
                total_lessons=len(c.lesson_ids)
            )
            for c in courses
        ]