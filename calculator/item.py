from dataclasses import dataclass
from contextlib import contextmanager

from . import BaseUnit, Tube, Pipe, Cut


@dataclass
class Item(BaseUnit):
    name: str
    base_price = 0.0
    base_area = 0.0
    sundries_count = 0
    sundry_welding_count = 0
    welding_length = 0.0
    riveting_count = 0
    bending_count = 0
    is_painted = False
    is_cleaned = False

    def __post_init__(self):
        self.tubes: list[Tube] = []
        self.items: list[Item] = []

    def __getitem__(self, key: int) -> Tube:
        return self.tubes[key]

    @property
    def price(self) -> float:
        result = 0.0

        result += sum(tube.price for tube in self.tubes)

        result += sum(item.price for item in self.items)

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
        result = self.base_area
        result += sum(tube.area for tube in self.tubes)
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
        item = Item(self.prices, self.multipliers, name)
        self.items.append(item)
        yield item
