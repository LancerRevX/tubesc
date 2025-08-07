from dataclasses import dataclass
from contextlib import contextmanager
from abc import ABC, abstractmethod

from . import BaseUnit, Tube, Pipe, Cut, Prices, Multipliers


@dataclass
class BaseItem:
    name: str
    project_hours: int = 0
    sundries_count: int = 0
    sundry_welding_count: int = 0
    welding_length: float = 0.0
    riveting_count: int = 0
    bending_count: int = 0
    is_painted = False
    is_cleaned = False
    price: float | None = None

    @property
    @abstractmethod
    def cutting_price(self) -> float:
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
        self, cutting_price: float, prices: Prices, multipliers: Multipliers
    ):
        pass


@dataclass
class TubeItem(BaseItem):
    def __post_init__(self):
        self.tubes: list[Tube] = []
        self.sheet_items: list[SheetItem] = []

    def __getitem__(self, key: int) -> Tube:
        return self.tubes[key]

    @property
    def incuts_count(self) -> int:
        return sum(tube.incuts_count for tube in self.tubes)

    @property
    def cutting_length(self) -> float:
        return sum(tube.cutting_length for tube in self.tubes)

    @property
    def cutting_price(self) -> float:
        return sum(tube.cutting_price for tube in self.tubes)

    def calculate_price(
        self, cutting_price: float, prices: Prices, multipliers: Multipliers
    ) -> None:
        for

        result = project_price + cutting_price

        result += sum(tube.price for tube in self.tubes)

        result += sum(item.price for item in self.sheet_items)

        welding = (
            self.welding_length * self.prices.welding
            + self.sundry_welding_count * 10 * self.prices.welding
        )
        work = (
            welding
            + self.riveting_count * self.prices.riveting
            + self.bending_count * self.prices.bending
        )

        if self.is_painted:
            work += self.area * self.prices.painting

        materials = self.base_price + self.sundries_count * self.prices.sundry

        result += (
            work * self.multipliers.work
            + materials * self.multipliers.materials
        )

        return result

    @property
    def area(self) -> float:
        result = sum(tube.area for tube in self.tubes)
        return result

    @contextmanager
    def add_tube(
        self, pipe: Pipe, length: float = 0.0, left_cut: Cut | None = None
    ):
        tube = Tube(self.prices, self.multipliers, pipe, length)
        if left_cut is not None:
            tube.left_cut = left_cut
        self.tubes.append(tube)
        yield tube

    @contextmanager
    def add_item(self, name: str):
        item = BaseItem(self.prices, self.multipliers, name)
        self.items.append(item)
        yield item


@dataclass
class SheetItem(BaseItem):
    sheet_price: float = 0.0
    area: float = 0.0
    sundries_count = 0
    sundry_welding_count = 0
