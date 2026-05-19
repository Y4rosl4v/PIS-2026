from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.application.service.course_service import CourseService
from app.application.command import (
    CreateCourseCommand,
    EnrollStudentCommand,
    CompleteLessonCommand,
    PassTestCommand
)
from app.application.query import (
    GetCourseByIdQuery,
    ListCoursesQuery,
    GetStudentProgressQuery
)
from app.infrastructure.config.database import get_db
from app.infrastructure.adapter.out.course_repository import CourseRepository
from app.infrastructure.adapter.out.enrollment_repository import EnrollmentRepository
from app.infrastructure.adapter.out.lesson_repository import LessonRepository
from app.infrastructure.adapter.out.event_publisher import RedisEventPublisher
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1", tags=["courses"])

# Request/Response DTOs
class CreateCourseRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)

class EnrollStudentRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    course_id: str = Field(..., min_length=1)

class CompleteLessonRequest(BaseModel):
    enrollment_id: str
    lesson_id: str

class PassTestRequest(BaseModel):
    enrollment_id: str
    lesson_id: str
    selected_option_index: int = Field(..., ge=0)

class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    rating: Optional[float]
    total_lessons: int

class EnrollmentResponse(BaseModel):
    id: str
    student_id: str
    course_id: str
    progress_percent: int
    is_completed: bool
    completed_lessons: List[str]

class LessonResponse(BaseModel):
    id: str
    title: str
    video_url: str
    has_test: bool

def get_course_service(db: Session = Depends(get_db)):
    """Dependency для получения CourseService"""
    repositories = {
        "course_repository": CourseRepository(db),
        "enrollment_repository": EnrollmentRepository(db),
        "lesson_repository": LessonRepository(db)
    }
    return CourseService(repositories, RedisEventPublisher())

# ========== COMMANDS (POST endpoints) ==========

@router.post("/courses", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_course(
    request: CreateCourseRequest,
    service: CourseService = Depends(get_course_service)
):
    """Создать новый курс"""
    command = CreateCourseCommand(request.title, request.description)
    course_id = service.create_course(command)
    return {"id": course_id, "message": "Course created successfully"}

@router.post("/enrollments", status_code=status.HTTP_201_CREATED, response_model=dict)
async def enroll_student(
    request: EnrollStudentRequest,
    service: CourseService = Depends(get_course_service)
):
    """Записать студента на курс"""
    command = EnrollStudentCommand(request.student_id, request.course_id)
    enrollment_id = service.enroll_student(command)
    return {"id": enrollment_id, "message": "Student enrolled successfully"}

@router.post("/enrollments/{enrollment_id}/lessons/{lesson_id}/complete", status_code=status.HTTP_200_OK)
async def complete_lesson(
    enrollment_id: str,
    lesson_id: str,
    service: CourseService = Depends(get_course_service)
):
    """Завершить урок"""
    command = CompleteLessonCommand(enrollment_id, lesson_id)
    service.complete_lesson(command)
    return {"message": "Lesson completed successfully"}

@router.post("/enrollments/{enrollment_id}/lessons/{lesson_id}/test", response_model=dict)
async def pass_test(
    enrollment_id: str,
    lesson_id: str,
    request: PassTestRequest,
    service: CourseService = Depends(get_course_service)
):
    """Пройти тест к уроку"""
    command = PassTestCommand(
        request.enrollment_id,
        request.lesson_id,
        request.selected_option_index
    )
    passed = service.pass_test(command)
    return {"passed": passed, "message": "Test completed"}

# ========== QUERIES (GET endpoints) ==========

@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    service: CourseService = Depends(get_course_service)
):
    """Получить курс по ID"""
    try:
        query = GetCourseByIdQuery(course_id)
        course = service.get_course_by_id(query)
        return CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            rating=course.rating,
            total_lessons=course.total_lessons
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/courses", response_model=List[CourseResponse])
async def list_courses(
    limit: int = 50,
    offset: int = 0,
    min_rating: Optional[float] = None,
    service: CourseService = Depends(get_course_service)
):
    """Получить список курсов"""
    query = ListCoursesQuery(limit, offset, min_rating)
    courses = service.list_courses(query)
    return [
        CourseResponse(
            id=c.id,
            title=c.title,
            description=c.description,
            rating=c.rating,
            total_lessons=c.total_lessons
        )
        for c in courses
    ]

@router.get("/students/{student_id}/progress/{course_id}", response_model=EnrollmentResponse)
async def get_student_progress(
    student_id: str,
    course_id: str,
    service: CourseService = Depends(get_course_service)
):
    """Получить прогресс студента по курсу"""
    query = GetStudentProgressQuery(student_id, course_id)
    progress = service.get_student_progress(query)
    return EnrollmentResponse(
        id=progress.id,
        student_id=progress.student_id,
        course_id=progress.course_id,
        progress_percent=progress.progress_percent,
        is_completed=progress.is_completed,
        completed_lessons=progress.completed_lessons
    )

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")