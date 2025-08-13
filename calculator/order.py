from dataclasses import dataclass, field
from contextlib import contextmanager

from . import BaseItem, Costs, Multipliers, TubeItem, SheetItem


@dataclass
class Order():
    number: int
    name: str
    minimum_cutting_cost: int = 500
    items: list[BaseItem] = field(default_factory=list[BaseItem])

    # def __post_init__(self) -> None:
    #     self.items: list[BaseItem] = []

    def __getitem__(self, key: int) -> BaseItem:
        return self.items[key]
    
    def __str__(self) -> str:
        result = f'Заказ №{self.number}\n'
        result += f'Резка: {self.cutting_length:,.2f} мм, {self.cutting_cost:,.2f} руб <= {self.adjusted_cutting_price:,.2f} руб\n'

        for item in self.items:
            result += str(item)
        return result

    @property
    def incuts_count(self) -> int:
        return sum(item.incuts_count for item in self.items)

    @property
    def cutting_length(self) -> float:
        return sum(item.cutting_length for item in self.items)

    @property
    def cutting_cost(self) -> float:
        return sum(item.cutting_cost * item.count for item in self.items)

    @property
    def adjusted_cutting_price(self) -> float:
        result = self.cutting_cost
        if result < self.minimum_cutting_cost:
            result = self.minimum_cutting_cost
        return result

    def calculate(self, costs: Costs, multipliers: Multipliers):
        cutting_price = self.cutting_cost
        adjusted_cutting_price = self.adjusted_cutting_price
        for item in self.items:
            item_cutting_price = (
                adjusted_cutting_price / cutting_price * item.cutting_cost
            )
            item.calculate_price(
                item_cutting_price, costs, multipliers
            )

    @contextmanager
    def add_tube_item(self, name: str):
        item = TubeItem(name)
        self.items.append(item)
        yield item

    @contextmanager
    def add_sheet_item(self, name: str):
        item = SheetItem(name, 0)
        self.items.append(item)
        yield item
