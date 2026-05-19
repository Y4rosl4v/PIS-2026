import grpc
from typing import List, Optional
import threading

from generated import course_service_pb2, course_service_pb2_grpc
from generated import common_pb2


class CourseServiceClient:
    """gRPC клиент для Course Service"""
    
    def __init__(self, channel: grpc.Channel):
        self.stub = course_service_pb2_grpc.CourseServiceStub(channel)
    
    def create_course(self, title: str, description: str) -> str:
        """Создание курса"""
        request = course_service_pb2.CreateCourseRequest(
            title=title,
            description=description
        )
        response = self.stub.CreateCourse(request)
        print(f"✅ Course created: {response.course_id}")
        print(f"   Status: {response.status.message}")
        return response.course_id
    
    def get_course(self, course_id: str) -> Optional[course_service_pb2.Course]:
        """Получение курса по ID"""
        try:
            request = course_service_pb2.GetCourseRequest(course_id=course_id)
            course = self.stub.GetCourse(request)
            print(f"📚 Course: {course.title}")
            print(f"   ID: {course.id}")
            print(f"   Lessons: {course.total_lessons}")
            print(f"   Students: {course.total_students}")
            return course
        except grpc.RpcError as e:
            print(f"❌ Error: {e.details()}")
            return None
    
    def list_courses(self, limit: int = 10, offset: int = 0, min_rating: Optional[float] = None) -> List[course_service_pb2.Course]:
        """Список курсов"""
        request = course_service_pb2.ListCoursesRequest(
            limit=limit,
            offset=offset
        )
        if min_rating is not None:
            request.min_rating = min_rating
        
        response = self.stub.ListCourses(request)
        print(f"📋 Found {response.total} courses")
        return list(response.courses)
    
    def update_rating(self, course_id: str, rating: float) -> Optional[course_service_pb2.Course]:
        """Обновление рейтинга курса"""
        request = course_service_pb2.UpdateRatingRequest(
            course_id=course_id,
            rating=rating
        )
        course = self.stub.UpdateRating(request)
        print(f"⭐ Rating updated for {course.title}: {rating}")
        return course
    
    def add_lesson(self, course_id: str, title: str, video_url: str) -> Optional[course_service_pb2.Lesson]:
        """Добавление урока"""
        request = course_service_pb2.AddLessonRequest(
            course_id=course_id,
            title=title,
            video_url=video_url
        )
        lesson = self.stub.AddLesson(request)
        print(f"📹 Lesson added: {lesson.title} (ID: {lesson.id})")
        return lesson
    
    def stream_course_updates(self, course_id: Optional[str] = None):
        """
        Server-side streaming: подписка на обновления курсов.
        Получает обновления в реальном времени.
        """
        request = course_service_pb2.StreamCourseRequest()
        if course_id:
            request.course_id = course_id
        
        print(f"🔔 Subscribed to course updates for: {course_id or 'ALL'}")
        
        try:
            for update in self.stub.StreamCourseUpdates(request):
                print(f"📢 Update received: {update.update_type}")
                print(f"   Course: {update.course_id}")
                print(f"   Time: {update.timestamp}")
                if update.HasField('course'):
                    print(f"   Title: {update.course.title}")
        except grpc.RpcError as e:
            print(f"Stream error: {e}")