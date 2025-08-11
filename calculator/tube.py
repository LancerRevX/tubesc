from dataclasses import dataclass, field

from . import Pipe, Hole, Cut, Costs, Multipliers, Price


@dataclass
class Tube:
    pipe: Pipe
    length: float
    is_ours: bool = True
    is_weld_cleaned: bool = False
    is_bended: bool = True
    is_cleaned: bool = False
    holes: list[Hole] = field(default_factory=list[Hole])
    left_cut: Cut | None = field(default_factory=Cut)
    right_cut: Cut | None = field(default_factory=Cut)
    extra_bending_count: int = 0
    bended_cuts: list[Cut] = field(default_factory=list[Cut])

    def __post_init__(self) -> None:
        self.price: Price | None = None

    def __str__(self) -> str:
        return f"{self.length} {self.pipe}"

    @property
    def bending_count(self) -> int:
        if not self.is_bended:
            return 0
        return len(self.bended_cuts) + self.extra_bending_count

    @property
    def pipe_cost(self) -> float:
        if not self.is_ours:
            return 0.0
        return self.pipe.cost * self.length
    
    @property
    def carrying_cost(self) -> float:
        return self.pipe.carrying_cost * self.length

    @property
    def cutting_cost(self) -> float:
        return (
            self.incuts_count * self.pipe.incut_cost
            + self.cutting_length * self.pipe.cutting_cost
        )

    @property
    def incuts_count(self) -> int:
        holes_count = 0
        for hole in self.holes:
            if hole.through:
                holes_count += hole.count * 2
            else:
                holes_count += hole.count
        return (
            (self.left_cut is not None)
            + (self.right_cut is not None)
            + holes_count
            + len(self.bended_cuts)
        )

    @property
    def cutting_length(self) -> float:
        result = 0.0
        for hole in self.holes:
            result += hole.length * hole.count * (2 if hole.through else 1)
        result += sum(
            self.pipe.get_bended_cut_length(cut) for cut in self.bended_cuts
        )
        if self.left_cut is not None:
            result += self.pipe.get_cut_length(self.left_cut)
        if self.right_cut is not None:
            result += self.pipe.get_cut_length(self.right_cut)
        return result

    @property
    def area(self) -> float:
        return self.length * self.pipe.perimeter

    @property
    def welding_length(self) -> float:
        result = 0.0
        if self.left_cut is not None:
            result += (
                self.pipe.get_cut_length(self.left_cut)
                * self.left_cut.welding_ratio
            )
        if self.right_cut is not None:
            result += (
                self.pipe.get_cut_length(self.right_cut)
                * self.right_cut.welding_ratio
            )
        result += sum(
            self.pipe.get_bended_cut_length(cut) / 2 for cut in self.bended_cuts
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

        materials = self.pipe_cost

        self.price = Price(
            cost=work + materials,
            final=(
                (work * multipliers.work + materials * multipliers.materials)
                * multipliers.manager
                * multipliers.vat
            ),
        )

    def add_hole(self, hole: Hole) -> None:
        self.holes.append(hole)

    def add_bended_cuts(self, cut: Cut, count: int = 1) -> None:
        for _ in range(count):
            self.bended_cuts.append(cut)
