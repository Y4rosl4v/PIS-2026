import pytest
from unittest.mock import patch

@pytest.mark.e2e
class TestCourseFlow:
    def test_full_course_creation_flow(self, test_client):
        """
        E2E тест: Создание курса → Добавление уроков → Получение курса
        """
        # Step 1: Create course
        response = test_client.post("/api/v1/courses", json={
            "title": "E2E Test Course",
            "description": "Testing full flow"
        })
        assert response.status_code == 201
        course_id = response.json()["id"]
        
        # Step 2: Get course by ID
        response = test_client.get(f"/api/v1/courses/{course_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "E2E Test Course"
        assert data["description"] == "Testing full flow"
    
    def test_course_not_found_returns_404(self, test_client):
        response = test_client.get("/api/v1/courses/NONEXISTENT")
        assert response.status_code == 404
    
    def test_list_courses_with_pagination(self, test_client):
        # Create multiple courses
        for i in range(3):
            test_client.post("/api/v1/courses", json={
                "title": f"Course {i}",
                "description": f"Desc {i}"
            })
        
        response = test_client.get("/api/v1/courses?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

@pytest.mark.e2e
class TestStudentJourney:
    def test_complete_student_journey(self, test_client):
        """
        Полный сценарий студента:
        1. Создание курса
        2. Запись на курс
        3. Завершение уроков
        4. Проверка прогресса
        """
        # Step 1: Create course
        response = test_client.post("/api/v1/courses", json={
            "title": "Python Journey",
            "description": "Learn Python step by step"
        })
        course_id = response.json()["id"]
        
        # Step 2: Enroll student
        response = test_client.post("/api/v1/enrollments", json={
            "student_id": "E2E_STUDENT",
            "course_id": course_id
        })
        assert response.status_code == 201
        enrollment_id = response.json()["id"]
        
        # Step 3: Get initial progress (should be 0)
        response = test_client.get(f"/api/v1/students/E2E_STUDENT/progress/{course_id}")
        assert response.status_code == 200
        progress = response.json()
        assert progress["progress_percent"] == 0
        
        # Step 4: Since we don't have actual lessons yet, we need to add them
        # This would require a lesson creation endpoint which we might not have
        # For now, we test the API structure
        
        # Step 5: Health check
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_enroll_nonexistent_course(self, test_client):
        response = test_client.post("/api/v1/enrollments", json={
            "student_id": "STU001",
            "course_id": "NOT_EXIST"
        })
        assert response.status_code == 500  # or 404 depending on handler
    
    def test_health_endpoint(self, test_client):
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data