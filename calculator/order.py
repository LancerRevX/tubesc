from dataclasses import dataclass, field

from . import Item, Prices


@dataclass
class Order:
    number: int
    name: str
    prices: Prices

    def __post_init__(self) -> None:
        self.items = []

    def __getitem__(self, key):
        return self.items[key]

    @property
    def price(self) -> float:
        return sum(item.price for item in self.items)

    def add_item(self, name: str) -> Item:
        item = Item(name, self.prices)
        self.items.append(item)
        return item
