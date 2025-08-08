from dataclasses import dataclass, field

from . import Pipe, Hole, Cut, Costs, Multipliers


@dataclass
class Tube:
    pipe: Pipe
    length: float
    is_ours: bool = True
    is_weld_cleaned: bool = False
    is_cleaned: bool = False
    holes: list[Hole] = field(default_factory=list[Hole])
    left_cut: Cut | None = field(default_factory=Cut)
    right_cut: Cut | None = field(default_factory=Cut)
    cost: float | None = None
    price: float | None = None

    def __str__(self) -> str:
        return f"{self.length} {self.pipe}: {self.cost} -> {self.price}"

    @property
    def cutting_cost(self) -> float:
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
    def area(self) -> float:
        return self.length * self.pipe.perimeter

    @property
    def welding_length(self) -> float:
        result = 0.0
        if self.left_cut is not None:
            result += (
                self.pipe.cut_length(self.left_cut)
                * self.left_cut.welding_ratio
            )
        if self.right_cut is not None:
            result += (
                self.pipe.cut_length(self.right_cut)
                * self.right_cut.welding_ratio
            )
        return result

    def calculate_price(
        self,
        cutting_cost: float,
        project_cost: float,
        costs: Costs,
        multipliers: Multipliers,
    ):
        work = cutting_cost + project_cost

        if self.is_weld_cleaned:
            work += self.length * costs.weld_cleaning

        if self.is_cleaned:
            work += self.area * costs.cleaning

        materials = 0.0
        if self.is_ours:
            materials = self.pipe.price * self.length

        self.cost = work + materials
        self.price = (
            (work * multipliers.work + materials * multipliers.materials)
            * multipliers.manager
            * multipliers.vat
        )

    def add_holes(self, hole: Hole, count: int = 1) -> None:
        for _ in range(count):
            self.holes.append(hole)
