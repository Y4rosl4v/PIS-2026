from dataclasses import dataclass
from typing import Optional

@dataclass
class LessonDTO:
    """DTO для чтения информации об уроке"""
    id: str
    title: str
    video_url: str
    has_test: bool