from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class CourseReadModel:
    """
    Денормализованная read-модель для курса.
    Содержит данные из Course + агрегированные данные из Enrollment.
    """
    id: str
    title: str
    description: str
    rating: Optional[float]
    
    # Денормализованные поля (агрегация)
    total_lessons: int
    total_students: int
    completed_students: int
    average_progress: float
    
    # Метаданные
    created_at: datetime
    updated_at: datetime

@dataclass
class CourseSummaryReadModel:
    """
    Упрощённая read-модель для списка курсов.
    """
    id: str
    title: str
    rating: Optional[float]
    total_students: int
    average_progress: float