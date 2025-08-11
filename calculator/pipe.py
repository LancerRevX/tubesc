from dataclasses import dataclass
from abc import ABC, abstractmethod
from math import sin, cos, pi

from . import Cut


@dataclass
class Pipe(ABC):
    cost: float
    thickness: float
    incut_cost: float
    cutting_cost: float
    carrying_cost: float

    @property
    @abstractmethod
    def perimeter(self) -> float:
        pass

    @abstractmethod
    def get_cut_length(self, cut: Cut) -> float:
        pass

    @abstractmethod
    def get_bended_cut_length(self, bended_cut: Cut) -> float:
        pass


@dataclass
class RoundPipe(Pipe):
    diameter: float

    def __str__(self) -> str:
        return f"D{self.diameter}x{self.thickness}"

    @property
    def perimeter(self) -> float:
        return self.diameter * pi

    def get_cut_length(self, cut: Cut):
        return self.perimeter / sin(cut.angle / 180 * pi)
    
    def get_bended_cut_length(self, bended_cut: Cut):
        return 0.0



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

    def get_cut_length(self, cut: Cut):
        if cut.angle == 90:
            return self.perimeter

        if cut.side == "width":
            hypotenuse = self.width / sin(cut.angle * 180 / pi)
            return (hypotenuse + self.height) * 2
        else:
            hypotenuse = self.height / sin(cut.angle * 180 / pi)
            return (hypotenuse + self.width) * 2
        
    def get_bended_cut_length(self, bended_cut: Cut):
        angle = bended_cut.angle // 2

        if bended_cut.side == "width":
            hypotenuse = self.width / sin(angle * 180 / pi)
            return (hypotenuse * 2 + self.height) * 2
        else:
            hypotenuse = self.height / sin(bended_cut.angle * 180 / pi)
            return (hypotenuse * 2 + self.width) * 2
