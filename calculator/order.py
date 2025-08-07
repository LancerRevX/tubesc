from dataclasses import dataclass
from contextlib import contextmanager

from . import BaseItem, BaseUnit


@dataclass
class Order(BaseUnit):
    number: int
    name: str
    minimum_cutting_price: int = 500

    def __post_init__(self) -> None:
        self.items: list[BaseItem] = []

    def __getitem__(self, key: int) -> BaseItem:
        return self.items[key]

    @property
    def incuts_count(self) -> int:
        return sum(item.incuts_count for item in self.items)

    @property
    def cutting_length(self) -> float:
        return sum(item.cutting_length for item in self.items)

    @property
    def cutting_price(self) -> float:
        return sum(item.cutting_price for item in self.items)

    @property
    def adjusted_cutting_price(self) -> float:
        result = self.cutting_price
        if result < self.minimum_cutting_price:
            result = self.minimum_cutting_price
        return result

    def calculate_price(self):
        cutting_price = self.cutting_price
        adjusted_cutting_price = self.adjusted_cutting_price
        for item in self.items:
            item_cutting_price = (
                adjusted_cutting_price / cutting_price * item.cutting_price
            )
            item.calculate_price(
                item_cutting_price, self.prices, self.multipliers
            )

    @contextmanager
    def add_item(self, name: str):
        item = BaseItem(self.prices, self.multipliers, name)
        self.items.append(item)
        yield item
