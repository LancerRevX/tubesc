from abc import ABC, abstractmethod

from calculator.costs import Costs
from calculator.item import BaseItem
from calculator.multipliers import Multipliers
from calculator.price import Price


class CalculationStrategy(ABC):
    @abstractmethod
    def calculate_price(self, object: object, costs: Costs, multipliers: Multipliers):
        pass


class PaintingStrategy(CalculationStrategy):
    NAME = "painting"

    def calculate_price(
        self, item: BaseItem, costs: Costs, multipliers: Multipliers
    ):
        if not item.is_painted:
            item.prices[self.NAME] = Price()
            return

        area = item.area
        work_cost = area * costs.painting
        paint_cost = area * costs.paint
        self.prices[self.NAME] = Price(
            cost=work_cost + paint_cost,
            final=(
                work_cost * multipliers.work
                + paint_cost * multipliers.materials
            )
            * multipliers.manager
            * multipliers.vat,
        )
