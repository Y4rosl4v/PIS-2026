from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CourseDTO:
    """DTO для чтения информации о курсе"""
    id: str
    title: str
    description: str
    rating: Optional[float]
    lesson_ids: List[str]
    total_lessons: int