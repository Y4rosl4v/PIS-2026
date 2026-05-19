from application.query import GetStudentProgressQuery
from application.query.dto import EnrollmentDTO

class GetStudentProgressHandler:
    """Обработчик запроса прогресса студента"""
    
    def __init__(self, enrollment_repository):
        self._enrollment_repository = enrollment_repository
    
    def handle(self, query: GetStudentProgressQuery) -> EnrollmentDTO:
        """Получить прогресс студента по курсу"""
        enrollment = self._enrollment_repository.find_by_student_and_course(
            query.student_id, query.course_id
        )
        
        if not enrollment:
            return EnrollmentDTO(
                id="",
                student_id=query.student_id,
                course_id=query.course_id,
                progress_percent=0,
                completed_lessons=[],
                is_completed=False
            )
        
        return EnrollmentDTO(
            id=enrollment.id,
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            progress_percent=enrollment.progress.value,
            completed_lessons=enrollment._completed_lessons.copy(),
            is_completed=enrollment.progress.is_completed()
        )