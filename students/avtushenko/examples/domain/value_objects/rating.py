from dataclasses import dataclass

@dataclass(frozen=True)
class Rating:
    """Value Object: Рейтинг курса (1-5)"""
    value: float

    def __post_init__(self):
        if not (1.0 <= self.value <= 5.0):
            raise ValueError(f"Rating must be between 1.0 and 5.0, got {self.value}")

    def as_stars(self) -> str:
        full = int(self.value)
        half = 1 if (self.value - full) >= 0.5 else 0
        empty = 5 - full - half
        return "★" * full + "½" * half + "☆" * empty