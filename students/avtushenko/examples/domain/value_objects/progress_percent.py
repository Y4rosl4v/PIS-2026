from dataclasses import dataclass

@dataclass(frozen=True)
class ProgressPercent:
    """Value Object: Прогресс в процентах (0-100)"""
    value: int

    def __post_init__(self):
        if not (0 <= self.value <= 100):
            raise ValueError(f"Progress must be between 0 and 100, got {self.value}")

    def as_float(self) -> float:
        return self.value / 100.0

    def is_completed(self) -> bool:
        return self.value == 100

    def __add__(self, other: "ProgressPercent") -> "ProgressPercent":
        new_value = min(100, self.value + other.value)
        return ProgressPercent(new_value)