from dataclasses import dataclass, KW_ONLY
from abc import ABC, abstractmethod
from math import pi


@dataclass
class Hole(ABC):
    _: KW_ONLY
    count: int = 1
    through: bool = False

    @property
    @abstractmethod
    def length(self) -> float:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass
class RoundHole(Hole):
    diameter: float = 0.0

    def __str__(self) -> str:
        return f'Отв. {"скв. " if self.through else ""}ф{self.diameter} - {self.count} шт'

    @property
    def length(self) -> float:
        return self.diameter * pi


@dataclass
class RectHole(Hole):
    width: float = 0.0
    height: float = 0.0

    def __str__(self) -> str:
        return f'Отв. {"скв. " if self.through else ""}{self.width}x{self.height} - {self.count} шт'

    @property
    def length(self) -> float:
        return (self.width + self.height) * 2


@dataclass
class CustomHole(Hole):
    length: float = 0.0 # pyright: ignore[reportIncompatibleMethodOverride]

    def __str__(self) -> str:
        return f'Отв. {"скв. " if self.through else ""}{self.length} - {self.count} шт'


__all__ = ["Hole", "RectHole", "RoundHole", "CustomHole"]
