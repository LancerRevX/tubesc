from dataclasses import dataclass
from typing import Literal

@dataclass
class Cut:
    angle: int = 90
    side: Literal['width', 'height'] | None = None
    welding_ratio: float = 0.0
    count: int = 1

    def __str__(self) -> str:
        return f'Рез {self.angle}°'