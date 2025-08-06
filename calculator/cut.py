from dataclasses import dataclass
from typing import Literal

@dataclass
class Cut:
    angle: int = 90
    side: Literal['width', 'height'] | None = None