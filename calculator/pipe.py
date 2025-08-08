from dataclasses import dataclass
from abc import ABC, abstractmethod
from math import sin, cos, pi

from . import Cut


@dataclass
class Pipe(ABC):
    price: float
    thickness: float
    incut_price: float
    cutting_price: float

    @property
    @abstractmethod
    def perimeter(self) -> float:
        pass

    @abstractmethod
    def cut_length(self, cut: Cut) -> float:
        pass


@dataclass
class RoundPipe(Pipe):
    diameter: float

    def __str__(self) -> str:
        return f"D{self.diameter}x{self.thickness}"

    @property
    def perimeter(self) -> float:
        return self.diameter * pi

    def cut_length(self, cut: Cut):
        return self.perimeter / cos(cut.angle / 180 * pi)


@dataclass
class RectPipe(Pipe):
    width: float
    height: float

    def __str__(self) -> str:
        first, second = sorted([self.width, self.height])
        return f"{first}x{second}x{self.thickness}"

    @property
    def perimeter(self) -> float:
        return (self.width + self.height) * 2

    def cut_length(self, cut: Cut):
        if cut.angle == 90:
            return self.perimeter

        if cut.side == "width":
            hypotenuse = self.width / sin(cut.angle * 180 / pi)
            return (hypotenuse + self.height) * 2
        else:
            hypotenuse = self.height / sin(cut.angle * 180 / pi)
            return (hypotenuse + self.width) * 2
