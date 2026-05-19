import pytest
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.config.database import Base, get_db
from app.infrastructure.adapter.out.course_repository import CourseRepository
from app.infrastructure.adapter.out.enrollment_repository import EnrollmentRepository
from app.infrastructure.adapter.out.lesson_repository import LessonRepository

class TestIntegration:
    
    @pytest.fixture(scope="class")
    def postgres_container(self):
        with PostgresContainer("postgres:15-alpine") as postgres:
            yield postgres
    
    @pytest.fixture
    def db_session(self, postgres_container):
        engine = create_engine(postgres_container.get_connection_url())
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def client(self, db_session):
        def override_get_db():
            yield db_session
        
        app.dependency_overrides[get_db] = override_get_db
        return TestClient(app)
    
    def test_create_course(self, client):
        response = client.post("/api/v1/courses", json={
            "title": "Test Course",
            "description": "Test Description"
        })
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["message"] == "Course created successfully"
    
    def test_get_course_by_id(self, client):
        # Create course first
        create_response = client.post("/api/v1/courses", json={
            "title": "Python Basics",
            "description": "Learn Python"
        })
        course_id = create_response.json()["id"]
        
        # Get course
        response = client.get(f"/api/v1/courses/{course_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Python Basics"
        assert data["description"] == "Learn Python"
    
    def test_get_nonexistent_course(self, client):
        response = client.get("/api/v1/courses/NONEXISTENT")
        assert response.status_code == 404
    
    def test_list_courses(self, client):
        # Create two courses
        client.post("/api/v1/courses", json={"title": "Course 1", "description": "Desc 1"})
        client.post("/api/v1/courses", json={"title": "Course 2", "description": "Desc 2"})
        
        response = client.get("/api/v1/courses?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_enroll_student(self, client):
        # Create course
        create_response = client.post("/api/v1/courses", json={
            "title": "Enrollment Test",
            "description": "Test"
        })
        course_id = create_response.json()["id"]
        
        # Enroll student
        response = client.post("/api/v1/enrollments", json={
            "student_id": "STUDENT_001",
            "course_id": course_id
        })
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
    
    def test_health_check(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"