import pytest
from unittest.mock import Mock, AsyncMock
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Фикстуры для тестов
@pytest.fixture
def mock_db_session():
    """Mock сессии БД"""
    session = Mock(spec=Session)
    return session

@pytest.fixture
def mock_event_publisher():
    """Mock публикатора событий"""
    publisher = Mock()
    publisher.publish = Mock()
    return publisher

# Фикстуры для тестов с реальной БД (интеграционные)
@pytest.fixture(scope="session")
def test_database_url():
    """URL тестовой БД (можно переопределить через env)"""
    import os
    return os.getenv("TEST_DATABASE_URL", "postgresql://testuser:testpass@localhost:5433/testdb")

@pytest.fixture(scope="function")
def db_session(test_database_url):
    """Сессия БД для интеграционных тестов"""
    from app.infrastructure.config.database import Base
    from app.infrastructure.config.models import CourseModel, LessonModel, EnrollmentModel
    
    engine = create_engine(test_database_url)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)

# Фикстуры для E2E тестов
@pytest.fixture(scope="module")
def test_client():
    """TestClient для E2E тестов"""
    from app.main import app
    return TestClient(app)

# Маркеры для pytest
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")