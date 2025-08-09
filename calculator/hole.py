from dataclasses import dataclass
from abc import ABC, abstractmethod
from math import pi


@dataclass
class Hole(ABC):
    @property
    @abstractmethod
    def length(self) -> float:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass
class RoundHole(Hole):
    diameter: float

    def __str__(self) -> str:
        return f'ф{self.diameter}'

    @property
    def length(self) -> float:
        return self.diameter * pi


@dataclass
class RectHole(Hole):
    width: float
    height: float

    def __str__(self) -> str:
        return f'{self.width}x{self.height}'

    @property
    def length(self) -> float:
        return (self.width + self.height) * 2


@dataclass
class CustomHole(Hole):
    length: float

    def __str__(self) -> str:
        return f'{self.length}'


__all__ = ["Hole", "RectHole", "RoundHole", "CustomHole"]
