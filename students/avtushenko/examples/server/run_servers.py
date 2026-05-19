#!/usr/bin/env python3
import grpc
from concurrent import futures
import logging

from generated import course_service_pb2_grpc, enrollment_service_pb2_grpc
from server.course_server import CourseServiceServicer
from server.enrollment_server import EnrollmentServiceServicer


def serve():
    """Запуск gRPC серверов"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Регистрируем сервисы
    course_service_pb2_grpc.add_CourseServiceServicer_to_server(
        CourseServiceServicer(), server
    )
    enrollment_service_pb2_grpc.add_EnrollmentServiceServicer_to_server(
        EnrollmentServiceServicer(), server
    )
    
    # Запускаем на портах
    server.add_insecure_port('[::]:50051')
    
    print("🚀 gRPC Server started on port 50051")
    print("📚 CourseService registered")
    print("📝 EnrollmentService registered")
    print("\nAvailable RPCs:")
    print("  - CourseService.CreateCourse")
    print("  - CourseService.GetCourse")
    print("  - CourseService.ListCourses")
    print("  - CourseService.StreamCourseUpdates (server streaming)")
    print("  - EnrollmentService.EnrollStudent")
    print("  - EnrollmentService.CompleteLesson")
    print("  - EnrollmentService.StreamProgress (server streaming)")
    print("  - EnrollmentService.BatchEnroll (client streaming)")
    print("  - EnrollmentService.InteractiveProgress (bidirectional streaming)")
    
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()