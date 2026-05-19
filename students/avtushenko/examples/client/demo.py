#!/usr/bin/env python3
import grpc
import time
import threading

from client.course_client import CourseServiceClient
from client.enrollment_client import EnrollmentServiceClient


def main():
    """Демонстрация работы gRPC клиентов"""
    
    # Подключение к gRPC серверу
    channel = grpc.insecure_channel('localhost:50051')
    course_client = CourseServiceClient(channel)
    enrollment_client = EnrollmentServiceClient(channel)
    
    print("=" * 60)
    print("🎓 Quick Courses - gRPC Demo")
    print("=" * 60)
    
    # 1. Создание курсов
    print("\n1️⃣ Creating courses...")
    course_id1 = course_client.create_course("Python Basics", "Learn Python from scratch")
    course_id2 = course_client.create_course("FastAPI Mastery", "Build APIs with FastAPI")
    time.sleep(0.5)
    
    # 2. Добавление уроков
    print("\n2️⃣ Adding lessons...")
    course_client.add_lesson(course_id1, "Introduction to Python", "https://youtu.be/abc123")
    course_client.add_lesson(course_id1, "Variables and Data Types", "https://youtu.be/def456")
    course_client.add_lesson(course_id2, "FastAPI First Endpoint", "https://youtu.be/ghi789")
    time.sleep(0.5)
    
    # 3. Запись студентов
    print("\n3️⃣ Enrolling students...")
    enrollment1 = enrollment_client.enroll_student("STU001", course_id1)
    enrollment2 = enrollment_client.enroll_student("STU002", course_id1)
    enrollment3 = enrollment_client.enroll_student("STU001", course_id2)
    time.sleep(0.5)
    
    # 4. Прохождение уроков
    print("\n4️⃣ Completing lessons...")
    enrollment_client.complete_lesson(enrollment1, "LSN-ABC123")  # Нужен реальный ID урока
    time.sleep(0.5)
    
    # 5. Получение прогресса
    print("\n5️⃣ Getting student progress...")
    progress = enrollment_client.get_student_progress("STU001")
    time.sleep(0.5)
    
    # 6. Список курсов
    print("\n6️⃣ Listing courses...")
    courses = course_client.list_courses()
    
    # 7. Server-side streaming (в отдельном потоке)
    print("\n7️⃣ Starting streaming (in background)...")
    def run_stream():
        course_client.stream_course_updates()
    stream_thread = threading.Thread(target=run_stream, daemon=True)
    stream_thread.start()
    
    # 8. Обновление рейтинга
    print("\n8️⃣ Updating rating...")
    course_client.update_rating(course_id1, 4.8)
    time.sleep(1)
    
    # 9. Client-side streaming (batch enroll)
    print("\n9️⃣ Batch enrollment...")
    batch = [
        ("STU010", course_id1),
        ("STU011", course_id1),
        ("STU012", course_id2),
        ("STU013", course_id1),
    ]
    enrollment_client.batch_enroll(batch)
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()