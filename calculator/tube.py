from dataclasses import dataclass, field

from . import BaseUnit, Pipe, Hole, Cut


@dataclass
class Tube:
    pipe: Pipe
    length: float
    is_weld_cleaned: bool = False
    is_cleaned: bool = False
    holes: list[Hole] = field(default_factory=list[Hole])
    left_cut: Cut | None = field(default_factory=Cut)
    right_cut: Cut | None = field(default_factory=Cut)

    @property
    def cutting_price(self) -> float:
        return (
            self.incuts_count * self.pipe.incut_price
            + self.cutting_length * self.pipe.cutting_price
        )

    @property
    def incuts_count(self) -> int:
        return (
            (self.left_cut is not None)
            + (self.right_cut is not None)
            + len(self.holes)
        )

    @property
    def cutting_length(self) -> float:
        result = sum(hole.cut_length for hole in self.holes)
        if self.left_cut is not None:
            result += self.pipe.cut_length(self.left_cut)
        if self.right_cut is not None:
            result += self.pipe.cut_length(self.right_cut)
        return result

    @property
    def price(self) -> float:
        def get_hole_price(hole: Hole):
            return (
                self.pipe.incut_price
                + hole.cut_length
                * self.pipe.cutting_price
                * self.multipliers.work
            )

        result = 0.0

        result += sum(get_hole_price(hole) for hole in self.holes)

        work = (
            self.pipe.incut_price
            + self.pipe.cut_length(self.left_cut) * self.pipe.cutting_price
        )
        work += (
            self.pipe.incut_price
            + self.pipe.cut_length(self.right_cut) * self.pipe.cutting_price
        )

        if self.is_weld_cleaned:
            work += self.length * self.prices.weld_cleaning

        if self.is_cleaned:
            work += self.area * self.prices.cleaning

        result += work * self.multipliers.work

        return result

    @property
    def area(self) -> float:
        return self.length * self.pipe.perimeter

    def add_holes(self, hole: Hole, count: int = 1) -> None:
        for _ in range(count):
            self.holes.append(hole)
