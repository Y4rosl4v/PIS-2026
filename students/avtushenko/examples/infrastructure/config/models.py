from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.infrastructure.config.database import Base

class CourseModel(Base):
    __tablename__ = "courses"

    id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lessons = relationship("LessonModel", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("EnrollmentModel", back_populates="course")

class LessonModel(Base):
    __tablename__ = "lessons"

    id = Column(String(50), primary_key=True)
    course_id = Column(String(50), ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    video_url = Column(String(500), nullable=False)
    test_question_text = Column(String(500), nullable=True)
    test_options = Column(JSON, nullable=True)  # List[str]
    test_correct_index = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("CourseModel", back_populates="lessons")

class EnrollmentModel(Base):
    __tablename__ = "enrollments"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), nullable=False, index=True)
    course_id = Column(String(50), ForeignKey("courses.id"), nullable=False)
    completed_lessons = Column(JSON, default=list)  # List[str]
    test_results = Column(JSON, default=dict)  # Dict[str, bool]
    total_lessons = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("CourseModel", back_populates="enrollments")

    @property
    def progress_percent(self) -> int:
        if self.total_lessons == 0:
            return 0
        return int((len(self.completed_lessons or []) / self.total_lessons) * 100)