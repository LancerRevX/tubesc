from dataclasses import dataclass, field
from contextlib import contextmanager
from abc import ABC, abstractmethod

from . import Tube, Costs, Multipliers, Pipe


@dataclass
class BaseItem(ABC):
    name: str
    project_hours: int = 0
    sundries_count: int = 0
    sundry_welding_count: int = 0
    riveting_count: int = 0
    bending_count: int = 0
    is_painted = False
    is_cleaned = False
    price: float | None = field(init=False, default=None)
    cost: float | None = field(init=False, default=None)

    @property
    @abstractmethod
    def cutting_cost(self) -> float:
        pass

    @property
    @abstractmethod
    def cutting_length(self) -> float:
        pass

    @property
    @abstractmethod
    def incuts_count(self) -> int:
        pass

    @abstractmethod
    def calculate_price(
        self,
        adjusted_cutting_cost: float,
        costs: Costs,
        multipliers: Multipliers,
    ):
        pass


@dataclass
class SheetItem(BaseItem):
    sheet_cost: float = 0.0
    area: float = 0.0
    welding_length: float = 0.0

    def __str__(self) -> str:
        return f'{self.name}: {self.cost} -> {self.price}'

    @property
    def incuts_count(self):
        return 0

    @property
    def cutting_length(self):
        return 0.0

    @property
    def cutting_cost(self):
        return 0.0

    def calculate_price(
        self,
        adjusted_cutting_cost: float,
        costs: Costs,
        multipliers: Multipliers,
    ):
        welding = (
            self.sundry_welding_count * 10 + self.welding_length
        ) * costs.welding
        work = (
            welding
            + self.riveting_count * costs.riveting
            + self.bending_count * costs.bending
        )
        materials = self.sheet_cost + self.sundries_count * costs.sundry

        if self.is_cleaned:
            work += self.area * costs.cleaning

        if self.is_painted:
            work += self.area * costs.painting
            materials += self.area * costs.paint

        self.cost = work + materials
        self.price = (
            (work * multipliers.work + materials * multipliers.materials)
            * multipliers.manager
            * multipliers.vat
        )


@dataclass
class TubeItem(BaseItem):
    def __post_init__(self):
        self.tubes: list[Tube] = []
        self.sheet_items: list[SheetItem] = []

    def __getitem__(self, key: int) -> Tube:
        return self.tubes[key]
    
    def __str__(self) -> str:
        result = f"{self.name}: {self.cost:,.2f} -> {self.price:,.2f}"
        for tube in self.tubes:
            result += f"\n\t{tube}"
        for sheet in self.sheet_items:
            result += f"\n\t{sheet}"
        return result

    @property
    def incuts_count(self) -> int:
        return sum(tube.incuts_count for tube in self.tubes)

    @property
    def cutting_length(self) -> float:
        return sum(tube.cutting_length for tube in self.tubes)

    @property
    def cutting_cost(self) -> float:
        return sum(tube.cutting_cost for tube in self.tubes)

    @property
    def welding_length(self) -> float:
        return sum(tube.welding_length for tube in self.tubes) + sum(
            sheet.welding_length for sheet in self.sheet_items
        )

    def calculate_price(
        self,
        adjusted_cutting_cost: float,
        costs: Costs,
        multipliers: Multipliers,
    ) -> None:
        for sheet in self.sheet_items:
            sheet.calculate_price(0.0, costs, multipliers)

        project_cost = self.project_hours * costs.project
        tube_project_cost = project_cost / len(self.tubes)

        cutting_cost = self.cutting_cost
        for tube in self.tubes:
            tube_cutting_cost = (
                adjusted_cutting_cost / cutting_cost * tube.cutting_cost
            )
            tube.calculate_price(
                tube_cutting_cost, tube_project_cost, costs, multipliers
            )

        welding = (
            self.welding_length + self.sundry_welding_count * 10
        ) * costs.welding
        work = (
            welding
            + self.riveting_count * costs.riveting
            + self.bending_count * costs.bending
        )

        materials = self.sundries_count * costs.sundry

        if self.is_painted:
            area = self.area
            work += area * costs.painting
            materials += area * costs.paint

        self.cost = (
            sum(tube.cost for tube in self.tubes if tube.cost)
            + work
            + materials
        )

        self.price = (
            (
                sum(tube.price for tube in self.tubes if tube.price)
                + work * multipliers.work
                + materials * multipliers.materials
            )
            * multipliers.manager
            * multipliers.vat
        )

    @property
    def area(self) -> float:
        result = sum(tube.area for tube in self.tubes)
        return result

    @contextmanager
    def add_tube(self, pipe: Pipe, length: float):
        tube = Tube(pipe, length)
        self.tubes.append(tube)
        yield tube

    @contextmanager
    def add_sheet_item(self, name: str):
        item = SheetItem(name)
        self.sheet_items.append(item)
        yield item
