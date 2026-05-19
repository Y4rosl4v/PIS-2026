import pytest
import grpc
from concurrent import futures

from generated import course_service_pb2, course_service_pb2_grpc
from server.course_server import CourseServiceServicer


@pytest.fixture
def grpc_channel():
    """Фикстура для создания gRPC канала"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    course_service_pb2_grpc.add_CourseServiceServicer_to_server(
        CourseServiceServicer(), server
    )
    port = server.add_insecure_port('[::]:0')
    server.start()
    
    channel = grpc.insecure_channel(f'localhost:{port}')
    yield channel
    
    server.stop(None)


class TestCourseService:
    
    def test_create_course(self, grpc_channel):
        stub = course_service_pb2_grpc.CourseServiceStub(grpc_channel)
        
        request = course_service_pb2.CreateCourseRequest(
            title="Test Course",
            description="Test Description"
        )
        
        response = stub.CreateCourse(request)
        
        assert response.course_id.startswith("CRS-")
        assert response.status.success is True
        assert response.status.code == 201
    
    def test_get_course(self, grpc_channel):
        stub = course_service_pb2_grpc.CourseServiceStub(grpc_channel)
        
        # Create course first
        create_req = course_service_pb2.CreateCourseRequest(
            title="Get Test",
            description="Desc"
        )
        create_resp = stub.CreateCourse(create_req)
        
        # Get course
        get_req = course_service_pb2.GetCourseRequest(course_id=create_resp.course_id)
        course = stub.GetCourse(get_req)
        
        assert course.id == create_resp.course_id
        assert course.title == "Get Test"
    
    def test_list_courses(self, grpc_channel):
        stub = course_service_pb2_grpc.CourseServiceStub(grpc_channel)
        
        request = course_service_pb2.ListCoursesRequest(limit=10, offset=0)
        response = stub.ListCourses(request)
        
        assert isinstance(response.total, int)
        assert isinstance(response.courses, list)