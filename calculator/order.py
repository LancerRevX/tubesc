from dataclasses import dataclass
from contextlib import contextmanager

from . import Item, BaseUnit


@dataclass
class Order(BaseUnit):
    number: int
    name: str

    def __post_init__(self) -> None:
        self.items: list[Item] = []

    def __getitem__(self, key: int) -> Item:
        return self.items[key]

    @property
    def price(self) -> float:
        return sum(item.price for item in self.items)

    @contextmanager
    def add_item(self, name: str):
        item = Item(self.prices, self.multipliers, name)
        self.items.append(item)
        yield item
