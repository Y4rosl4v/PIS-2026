import grpc
from concurrent import futures
import uuid
from datetime import datetime
from typing import Dict, List, Set, Optional
import asyncio

from generated import enrollment_service_pb2, enrollment_service_pb2_grpc
from generated import common_pb2

# In-memory storage
enrollments_db: Dict[str, dict] = {}

# Хранилище для streaming подписчиков
progress_subscribers: Dict[str, Set[grpc.ServicerContext]] = {}


class EnrollmentServiceServicer(enrollment_service_pb2_grpc.EnrollmentServiceServicer):
    """Реализация gRPC сервиса записей и прогресса"""
    
    def EnrollStudent(self, request, context):
        """Запись студента на курс (Unary RPC)"""
        # Проверяем, не записан ли уже
        for enrollment in enrollments_db.values():
            if enrollment["student_id"] == request.student_id and enrollment["course_id"] == request.course_id:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Student already enrolled")
                return enrollment_service_pb2.EnrollStudentResponse()
        
        enrollment_id = f"ENR-{uuid.uuid4().hex[:8].upper()}"
        
        enrollment = {
            "id": enrollment_id,
            "student_id": request.student_id,
            "course_id": request.course_id,
            "progress": 0,
            "completed_lessons": [],
            "is_completed": False,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "updated_at": datetime.now().isoformat()
        }
        enrollments_db[enrollment_id] = enrollment
        
        return enrollment_service_pb2.EnrollStudentResponse(
            enrollment_id=enrollment_id,
            status=common_pb2.Status(success=True, message="Student enrolled", code=201)
        )
    
    def GetEnrollment(self, request, context):
        """Получение записи по ID (Unary RPC)"""
        enrollment = enrollments_db.get(request.enrollment_id)
        if not enrollment:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return enrollment_service_pb2.Enrollment()
        
        return self._to_proto_enrollment(enrollment)
    
    def GetStudentProgress(self, request, context):
        """Получение прогресса студента (Unary RPC)"""
        student_enrollments = [
            e for e in enrollments_db.values()
            if e["student_id"] == request.student_id
        ]
        
        # Фильтрация по курсу
        if request.HasField('course_id'):
            student_enrollments = [e for e in student_enrollments if e["course_id"] == request.course_id]
        
        courses_progress = []
        for enrollment in student_enrollments:
            courses_progress.append(enrollment_service_pb2.CourseProgress(
                course_id=enrollment["course_id"],
                course_title=f"Course {enrollment['course_id']}",  # В реальности запрос к Course Service
                progress=common_pb2.Progress(
                    percent=enrollment["progress"],
                    completed_lessons=enrollment["completed_lessons"],
                    is_completed=enrollment["is_completed"]
                ),
                started_at=enrollment["started_at"],
                completed_at=enrollment.get("completed_at"),
                last_activity=enrollment["updated_at"]
            ))
        
        if courses_progress:
            avg_progress = sum(c.progress.percent for c in courses_progress) / len(courses_progress)
            completed = sum(1 for c in courses_progress if c.progress.is_completed)
        else:
            avg_progress = 0
            completed = 0
        
        return enrollment_service_pb2.StudentProgress(
            student_id=request.student_id,
            courses=courses_progress,
            average_progress=avg_progress,
            total_courses=len(courses_progress),
            completed_courses=completed
        )
    
    def CompleteLesson(self, request, context):
        """Завершение урока (Unary RPC)"""
        enrollment = enrollments_db.get(request.enrollment_id)
        if not enrollment:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return enrollment_service_pb2.CompleteLessonResponse(success=False)
        
        if request.lesson_id in enrollment["completed_lessons"]:
            return enrollment_service_pb2.CompleteLessonResponse(
                success=False,
                message="Lesson already completed",
                new_progress=enrollment["progress"]
            )
        
        enrollment["completed_lessons"].append(request.lesson_id)
        
        # Обновляем прогресс (total_lessons = 10 для примера)
        total_lessons = 10
        enrollment["progress"] = int(len(enrollment["completed_lessons"]) / total_lessons * 100)
        enrollment["updated_at"] = datetime.now().isoformat()
        
        if enrollment["progress"] == 100:
            enrollment["is_completed"] = True
            enrollment["completed_at"] = datetime.now().isoformat()
        
        # Уведомляем подписчиков
        self._notify_progress_subscribers(
            enrollment["student_id"],
            enrollment["course_id"],
            enrollment["progress"],
            request.lesson_id
        )
        
        return enrollment_service_pb2.CompleteLessonResponse(
            success=True,
            new_progress=enrollment["progress"],
            message="Lesson completed"
        )
    
    def PassTest(self, request, context):
        """Прохождение теста (Unary RPC)"""
        enrollment = enrollments_db.get(request.enrollment_id)
        if not enrollment:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return enrollment_service_pb2.PassTestResponse(passed=False)
        
        # Проверяем, завершён ли урок
        if request.lesson_id not in enrollment["completed_lessons"]:
            return enrollment_service_pb2.PassTestResponse(
                passed=False,
                message="Complete the lesson first"
            )
        
        # В реальности здесь проверка с правильным ответом
        passed = request.selected_option == 0  # Для примера
        
        return enrollment_service_pb2.PassTestResponse(
            passed=passed,
            message="Test passed!" if passed else "Test failed. Try again."
        )
    
    def StreamProgress(self, request, context):
        """
        Server-side streaming: отслеживание прогресса в реальном времени.
        Клиент получает обновления при каждом завершении урока.
        """
        student_id = request.student_id
        course_id = request.course_id if request.HasField('course_id') else None
        
        # Регистрируем подписчика
        key = f"{student_id}:{course_id}" if course_id else student_id
        if key not in progress_subscribers:
            progress_subscribers[key] = set()
        progress_subscribers[key].add(context)
        
        try:
            # Отправляем текущий прогресс
            for enrollment in enrollments_db.values():
                if enrollment["student_id"] == student_id:
                    if not course_id or enrollment["course_id"] == course_id:
                        yield enrollment_service_pb2.ProgressUpdate(
                            enrollment_id=enrollment["id"],
                            student_id=enrollment["student_id"],
                            course_id=enrollment["course_id"],
                            course_title=f"Course {enrollment['course_id']}",
                            progress_percent=enrollment["progress"],
                            last_completed_lesson=enrollment["completed_lessons"][-1] if enrollment["completed_lessons"] else "",
                            timestamp=enrollment["updated_at"]
                        )
            
            # Держим соединение
            while context.is_active():
                await asyncio.sleep(0.1)
        finally:
            progress_subscribers[key].discard(context)
            if not progress_subscribers[key]:
                del progress_subscribers[key]
    
    def BatchEnroll(self, request_iterator, context):
        """
        Client-side streaming: массовая запись студентов.
        Принимает поток запросов, возвращает один ответ.
        """
        total = 0
        succeeded = 0
        errors = []
        
        for request in request_iterator:
            total += 1
            try:
                # Проверяем дубликаты
                exists = any(
                    e["student_id"] == request.student_id and e["course_id"] == request.course_id
                    for e in enrollments_db.values()
                )
                if exists:
                    errors.append(enrollment_service_pb2.EnrollmentError(
                        student_id=request.student_id,
                        course_id=request.course_id,
                        error="Already enrolled"
                    ))
                    continue
                
                enrollment_id = f"ENR-{uuid.uuid4().hex[:8].upper()}"
                enrollments_db[enrollment_id] = {
                    "id": enrollment_id,
                    "student_id": request.student_id,
                    "course_id": request.course_id,
                    "progress": 0,
                    "completed_lessons": [],
                    "is_completed": False,
                    "started_at": datetime.now().isoformat(),
                    "completed_at": None,
                    "updated_at": datetime.now().isoformat()
                }
                succeeded += 1
            except Exception as e:
                errors.append(enrollment_service_pb2.EnrollmentError(
                    student_id=request.student_id,
                    course_id=request.course_id,
                    error=str(e)
                ))
        
        return enrollment_service_pb2.BatchEnrollResponse(
            total=total,
            succeeded=succeeded,
            failed=total - succeeded,
            errors=errors
        )
    
    def InteractiveProgress(self, request_iterator, context):
        """
        Bidirectional streaming: интерактивное отслеживание прогресса.
        Клиент отправляет команды, сервер отвечает обновлениями.
        """
        tracked_students = set()
        
        for command in request_iterator:
            if command.HasField('start'):
                student_id = command.start.student_id
                course_id = command.start.course_id
                tracked_students.add((student_id, course_id))
                
                # Отправляем текущий прогресс
                for enrollment in enrollments_db.values():
                    if enrollment["student_id"] == student_id and enrollment["course_id"] == course_id:
                        yield enrollment_service_pb2.ProgressUpdate(
                            enrollment_id=enrollment["id"],
                            student_id=student_id,
                            course_id=course_id,
                            course_title=f"Course {course_id}",
                            progress_percent=enrollment["progress"],
                            last_completed_lesson="",
                            timestamp=datetime.now().isoformat()
                        )
            
            elif command.HasField('stop'):
                student_id = command.stop.student_id
                tracked_students.discard((student_id, command.stop.course_id) 
                                        if hasattr(command.stop, 'course_id') else (student_id, None))
            
            elif command.HasField('status'):
                student_id = command.status.student_id
                for enrollment in enrollments_db.values():
                    if enrollment["student_id"] == student_id:
                        yield enrollment_service_pb2.ProgressUpdate(
                            enrollment_id=enrollment["id"],
                            student_id=student_id,
                            course_id=enrollment["course_id"],
                            course_title=f"Course {enrollment['course_id']}",
                            progress_percent=enrollment["progress"],
                            last_completed_lesson=enrollment["completed_lessons"][-1] if enrollment["completed_lessons"] else "",
                            timestamp=enrollment["updated_at"]
                        )
    
    def _notify_progress_subscribers(self, student_id: str, course_id: str, progress: int, last_lesson: str):
        """Уведомление подписчиков об изменении прогресса"""
        update = enrollment_service_pb2.ProgressUpdate(
            student_id=student_id,
            course_id=course_id,
            course_title=f"Course {course_id}",
            progress_percent=progress,
            last_completed_lesson=last_lesson,
            timestamp=datetime.now().isoformat()
        )
        
        # Уведомляем специфичных подписчиков
        specific_key = f"{student_id}:{course_id}"
        if specific_key in progress_subscribers:
            for subscriber in progress_subscribers[specific_key]:
                try:
                    subscriber.send(update)
                except Exception:
                    pass
        
        # Уведомляем общих подписчиков
        general_key = student_id
        if general_key in progress_subscribers:
            for subscriber in progress_subscribers[general_key]:
                try:
                    subscriber.send(update)
                except Exception:
                    pass
    
    def _to_proto_enrollment(self, enrollment: dict) -> enrollment_service_pb2.Enrollment:
        """Конвертация внутреннего объекта в protobuf Enrollment"""
        return enrollment_service_pb2.Enrollment(
            id=enrollment["id"],
            student_id=enrollment["student_id"],
            course_id=enrollment["course_id"],
            progress=common_pb2.Progress(
                percent=enrollment["progress"],
                completed_lessons=enrollment["completed_lessons"],
                is_completed=enrollment["is_completed"]
            ),
            started_at=enrollment["started_at"],
            completed_at=enrollment.get("completed_at"),
            updated_at=enrollment["updated_at"]
        )