from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ListCoursesQuery:
    """Запрос для получения списка курсов"""
    limit: int = 50
    offset: int = 0
    min_rating: Optional[float] = None
    
    def __post_init__(self):
        if self.limit < 1 or self.limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        if self.offset < 0:
            raise ValueError("Offset must be >= 0")
        if self.min_rating is not None and not (1 <= self.min_rating <= 5):
            raise ValueError("Min rating must be between 1 and 5")