import grpc
from typing import List, Optional
import threading

from generated import enrollment_service_pb2, enrollment_service_pb2_grpc


class EnrollmentServiceClient:
    """gRPC клиент для Enrollment Service"""
    
    def __init__(self, channel: grpc.Channel):
        self.stub = enrollment_service_pb2_grpc.EnrollmentServiceStub(channel)
    
    def enroll_student(self, student_id: str, course_id: str) -> Optional[str]:
        """Запись студента на курс"""
        request = enrollment_service_pb2.EnrollStudentRequest(
            student_id=student_id,
            course_id=course_id
        )
        response = self.stub.EnrollStudent(request)
        if response.status.success:
            print(f"✅ Student {student_id} enrolled to {course_id}")
            print(f"   Enrollment ID: {response.enrollment_id}")
            return response.enrollment_id
        else:
            print(f"❌ Enrollment failed: {response.status.message}")
            return None
    
    def get_enrollment(self, enrollment_id: str) -> Optional[enrollment_service_pb2.Enrollment]:
        """Получение записи по ID"""
        request = enrollment_service_pb2.GetEnrollmentRequest(enrollment_id=enrollment_id)
        try:
            enrollment = self.stub.GetEnrollment(request)
            print(f"📝 Enrollment: {enrollment.id}")
            print(f"   Progress: {enrollment.progress.percent}%")
            print(f"   Completed: {len(enrollment.progress.completed_lessons)} lessons")
            return enrollment
        except grpc.RpcError as e:
            print(f"❌ Error: {e.details()}")
            return None
    
    def get_student_progress(self, student_id: str, course_id: Optional[str] = None) -> enrollment_service_pb2.StudentProgress:
        """Получение прогресса студента"""
        request = enrollment_service_pb2.GetStudentProgressRequest(student_id=student_id)
        if course_id:
            request.course_id = course_id
        
        progress = self.stub.GetStudentProgress(request)
        print(f"📊 Student {student_id} progress:")
        print(f"   Average: {progress.average_progress}%")
        print(f"   Completed: {progress.completed_courses}/{progress.total_courses} courses")
        return progress
    
    def complete_lesson(self, enrollment_id: str, lesson_id: str) -> bool:
        """Завершение урока"""
        request = enrollment_service_pb2.CompleteLessonRequest(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id
        )
        response = self.stub.CompleteLesson(request)
        if response.success:
            print(f"✅ Lesson {lesson_id} completed!")
            print(f"   New progress: {response.new_progress}%")
        else:
            print(f"❌ {response.message}")
        return response.success
    
    def pass_test(self, enrollment_id: str, lesson_id: str, selected_option: int) -> bool:
        """Прохождение теста"""
        request = enrollment_service_pb2.PassTestRequest(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
            selected_option=selected_option
        )
        response = self.stub.PassTest(request)
        if response.passed:
            print(f"🎉 {response.message}")
        else:
            print(f"❌ {response.message}")
        return response.passed
    
    def stream_progress(self, student_id: str, course_id: Optional[str] = None):
        """
        Server-side streaming: отслеживание прогресса в реальном времени.
        Получает обновления при каждом завершении урока.
        """
        request = enrollment_service_pb2.StreamProgressRequest(student_id=student_id)
        if course_id:
            request.course_id = course_id
        
        print(f"🔔 Tracking progress for student {student_id}")
        
        try:
            for update in self.stub.StreamProgress(request):
                print(f"\n📈 Progress update:")
                print(f"   Course: {update.course_title}")
                print(f"   Progress: {update.progress_percent}%")
                print(f"   Last lesson: {update.last_completed_lesson}")
                print(f"   Time: {update.timestamp}")
        except grpc.RpcError as e:
            print(f"Stream error: {e}")
    
    def batch_enroll(self, enrollments: List[tuple]) -> enrollment_service_pb2.BatchEnrollResponse:
        """
        Client-side streaming: массовая запись студентов.
        Отправляет поток запросов, получает один ответ.
        """
        def request_generator():
            for student_id, course_id in enrollments:
                yield enrollment_service_pb2.EnrollStudentRequest(
                    student_id=student_id,
                    course_id=course_id
                )
        
        response = self.stub.BatchEnroll(request_generator())
        print(f"📦 Batch enrollment completed:")
        print(f"   Total: {response.total}")
        print(f"   Succeeded: {response.succeeded}")
        print(f"   Failed: {response.failed}")
        for error in response.errors:
            print(f"   ✗ {error.student_id} -> {error.error}")
        return response
    
    def interactive_progress(self, student_id: str, course_id: str):
        """
        Bidirectional streaming: интерактивное отслеживание прогресса.
        Отправляет команды, получает обновления.
        """
        def command_generator():
            # Начинаем отслеживание
            yield enrollment_service_pb2.ProgressCommand(
                start=enrollment_service_pb2.StartTracking(
                    student_id=student_id,
                    course_id=course_id
                )
            )
            
            # Запрашиваем статус
            yield enrollment_service_pb2.ProgressCommand(
                status=enrollment_service_pb2.GetStatus(student_id=student_id)
            )
            
            # Ждём команды из консоли
            while True:
                cmd = input("\nCommand (status/stop/quit): ").strip().lower()
                if cmd == "status":
                    yield enrollment_service_pb2.ProgressCommand(
                        status=enrollment_service_pb2.GetStatus(student_id=student_id)
                    )
                elif cmd == "stop":
                    yield enrollment_service_pb2.ProgressCommand(
                        stop=enrollment_service_pb2.StopTracking(student_id=student_id)
                    )
                    break
                elif cmd == "quit":
                    break
        
        print(f"🎮 Interactive progress mode for {student_id}")
        print("Commands: status, stop, quit")
        
        try:
            for update in self.stub.InteractiveProgress(command_generator()):
                print(f"\n📊 Progress: {update.progress_percent}%")
                print(f"   Course: {update.course_title}")
                if update.last_completed_lesson:
                    print(f"   Last completed: {update.last_completed_lesson}")
        except grpc.RpcError as e:
            print(f"Error: {e}")