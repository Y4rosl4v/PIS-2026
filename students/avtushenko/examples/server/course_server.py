import grpc
from concurrent import futures
import uuid
from datetime import datetime
from typing import Dict, List, Set, Optional
import asyncio

from generated import course_service_pb2, course_service_pb2_grpc
from generated import common_pb2

# In-memory storage (в реальном проекте - БД)
courses_db: Dict[str, dict] = {}
lessons_db: Dict[str, dict] = {}

# Хранилище для streaming подписчиков
course_subscribers: Set[grpc.ServicerContext] = set()


class CourseServiceServicer(course_service_pb2_grpc.CourseServiceServicer):
    """Реализация gRPC сервиса курсов"""
    
    def CreateCourse(self, request, context):
        """Создание курса (Unary RPC)"""
        course_id = f"CRS-{uuid.uuid4().hex[:8].upper()}"
        
        course = {
            "id": course_id,
            "title": request.title,
            "description": request.description,
            "rating": None,
            "lessons": [],
            "total_lessons": 0,
            "total_students": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        courses_db[course_id] = course
        
        # Уведомляем подписчиков о создании курса
        self._notify_subscribers(course_id, "COURSE_CREATED", course=course)
        
        return course_service_pb2.CreateCourseResponse(
            course_id=course_id,
            status=common_pb2.Status(success=True, message="Course created", code=201)
        )
    
    def GetCourse(self, request, context):
        """Получение курса по ID (Unary RPC)"""
        course = courses_db.get(request.course_id)
        if not course:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Course {request.course_id} not found")
            return course_service_pb2.Course()
        
        return self._to_proto_course(course)
    
    def ListCourses(self, request, context):
        """Список курсов с пагинацией (Unary RPC)"""
        courses = list(courses_db.values())
        
        # Фильтрация по рейтингу
        if request.HasField('min_rating'):
            courses = [c for c in courses if c.get("rating") and c["rating"] >= request.min_rating]
        
        total = len(courses)
        
        # Пагинация
        start = request.offset
        end = start + request.limit
        paginated = courses[start:end]
        
        return course_service_pb2.ListCoursesResponse(
            courses=[self._to_proto_course(c) for c in paginated],
            total=total
        )
    
    def UpdateRating(self, request, context):
        """Обновление рейтинга курса (Unary RPC)"""
        course = courses_db.get(request.course_id)
        if not course:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return course_service_pb2.Course()
        
        course["rating"] = request.rating
        course["updated_at"] = datetime.now().isoformat()
        
        self._notify_subscribers(request.course_id, "RATING_CHANGED", 
                                 new_rating=request.rating)
        
        return self._to_proto_course(course)
    
    def AddLesson(self, request, context):
        """Добавление урока в курс (Unary RPC)"""
        course = courses_db.get(request.course_id)
        if not course:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return course_service_pb2.Lesson()
        
        lesson_id = f"LSN-{uuid.uuid4().hex[:8].upper()}"
        
        test = None
        if request.HasField('test'):
            test = request.test
        
        lesson = {
            "id": lesson_id,
            "course_id": request.course_id,
            "title": request.title,
            "video_url": request.video_url,
            "test": test,
            "created_at": datetime.now().isoformat()
        }
        
        lessons_db[lesson_id] = lesson
        course["lessons"].append(lesson_id)
        course["total_lessons"] += 1
        course["updated_at"] = datetime.now().isoformat()
        
        self._notify_subscribers(request.course_id, "COURSE_UPDATED", course=course)
        
        return self._to_proto_lesson(lesson)
    
    def StreamCourseUpdates(self, request, context):
        """
        Server-side streaming: отправка обновлений курсов в реальном времени.
        Клиент подписывается и получает все изменения.
        """
        # Добавляем клиента в подписчики
        course_subscribers.add(context)
        
        try:
            # Отправляем текущее состояние
            for course_id, course in courses_db.items():
                if not request.course_id or request.course_id == course_id:
                    yield self._create_update(
                        course_id, "COURSE_UPDATED", course=course
                    )
            
            # Держим соединение открытым
            while not context.is_active():
                await asyncio.sleep(0.1)
        finally:
            course_subscribers.discard(context)
    
    def _notify_subscribers(self, course_id: str, update_type: str, **kwargs):
        """Уведомление всех подписчиков об изменении"""
        update = self._create_update(course_id, update_type, **kwargs)
        dead_subscribers = set()
        
        for subscriber in course_subscribers:
            try:
                subscriber.send(update)
            except Exception:
                dead_subscribers.add(subscriber)
        
        # Удаляем мёртвых подписчиков
        for dead in dead_subscribers:
            course_subscribers.discard(dead)
    
    def _create_update(self, course_id: str, update_type: str, **kwargs):
        """Создание объекта CourseUpdate"""
        type_map = {
            "COURSE_CREATED": course_service_pb2.COURSE_CREATED,
            "COURSE_UPDATED": course_service_pb2.COURSE_UPDATED,
            "RATING_CHANGED": course_service_pb2.RATING_CHANGED,
            "STUDENT_ENROLLED": course_service_pb2.STUDENT_ENROLLED,
        }
        
        update = course_service_pb2.CourseUpdate(
            course_id=course_id,
            update_type=type_map.get(update_type, course_service_pb2.COURSE_UPDATED),
            timestamp=datetime.now().isoformat()
        )
        
        if "course" in kwargs:
            update.course.CopyFrom(self._to_proto_course(kwargs["course"]))
        if "new_rating" in kwargs:
            update.new_rating = kwargs["new_rating"]
        if "new_total_students" in kwargs:
            update.new_total_students = kwargs["new_total_students"]
        
        return update
    
    def _to_proto_course(self, course: dict) -> course_service_pb2.Course:
        """Конвертация внутреннего объекта в protobuf Course"""
        lessons = []
        for lesson_id in course.get("lessons", []):
            lesson = lessons_db.get(lesson_id)
            if lesson:
                lessons.append(self._to_proto_lesson(lesson))
        
        return course_service_pb2.Course(
            id=course["id"],
            title=course["title"],
            description=course["description"],
            rating=course.get("rating") if course.get("rating") else None,
            lessons=lessons,
            total_lessons=course.get("total_lessons", 0),
            total_students=course.get("total_students", 0),
            created_at=course.get("created_at", ""),
            updated_at=course.get("updated_at", "")
        )
    
    def _to_proto_lesson(self, lesson: dict) -> course_service_pb2.Lesson:
        """Конвертация внутреннего объекта в protobuf Lesson"""
        test = None
        if lesson.get("test"):
            test = course_service_pb2.TestQuestion(
                text=lesson["test"].text,
                options=lesson["test"].options,
                correct_option_index=lesson["test"].correct_option_index
            )
        
        return course_service_pb2.Lesson(
            id=lesson["id"],
            course_id=lesson["course_id"],
            title=lesson["title"],
            video_url=lesson["video_url"],
            test=test,
            created_at=lesson.get("created_at", "")
        )