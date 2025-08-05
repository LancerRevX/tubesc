from dataclasses import dataclass
from abc import ABC, abstractmethod
from math import pi
from typing import Literal, Optional


@dataclass
class Pipe(ABC):
    price: float

    @abstractmethod
    def perimeter(self):
        pass

    @abstractmethod
    def cut_length(
        self, angle: int, side: Optional[Literal["width", "height"]]
    ):
        pass


@dataclass
class RoundPipe:
    diameter: float

    def perimeter(self):
        return self.diameter * pi
    
    def cut_length(self, angle: int):
        pass
