from dataclasses import dataclass
from abc import ABC, abstractmethod
from math import pi


@dataclass
class Hole(ABC):
    @property
    @abstractmethod
    def cut_length(self) -> float:
        pass


@dataclass
class RoundHole(Hole):
    diameter: float

    @property
    def cut_length(self) -> float:
        return self.diameter * pi


@dataclass
class RectHole(Hole):
    width: float
    height: float

    @property
    def cut_length(self) -> float:
        return (self.width + self.height) * 2


@dataclass
class CustomHole(Hole):
    length: float

    @property
    def cut_length(self) -> float:
        return self.length


__all__ = ["Hole", "RectHole", "RoundHole", "CustomHole"]
