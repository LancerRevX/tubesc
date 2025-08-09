from dataclasses import dataclass  # field
from contextlib import contextmanager
from abc import ABC, abstractmethod

from . import Tube, Costs, Multipliers, Pipe, Price


@dataclass
class BaseItem(ABC):
    name: str
    project_hours: int = 0
    sundry_welding_count: int = 0
    is_painted: bool = False
    is_cleaned: bool = False
    transport_cost: float = 0.0
    is_weld_cleaned: bool = False

    def __post_init__(self) -> None:
        self.prices: dict[str, Price] = dict()

    @property
    @abstractmethod
    def area(self) -> float:
        pass

    @property
    @abstractmethod
    def welding_length(self) -> float:
        pass

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

    @property
    @abstractmethod
    def bending_count(self) -> int:
        pass

    @property
    @abstractmethod
    def sundries_count(self) -> int:
        pass

    @property
    @abstractmethod
    def riveting_count(self) -> int:
        pass

    @abstractmethod
    def calculate_price(
        self,
        adjusted_cutting_cost: float,
        costs: Costs,
        multipliers: Multipliers,
    ):
        pass

    def calculate_painting_price(self, costs: Costs, multipliers: Multipliers):
        area = self.area
        work_cost = area * costs.painting
        paint_cost = area * costs.paint
        self.prices["painting"] = Price(
            cost=work_cost + paint_cost,
            final=(
                work_cost * multipliers.work
                + paint_cost * multipliers.materials
            )
            * multipliers.manager
            * multipliers.vat,
        )

    def calculate_welding_price(self, costs: Costs, multipliers: Multipliers):
        welding_cost = self.welding_length * costs.welding
        self.prices["welding"] = self.get_work_price(welding_cost, multipliers)

    def calculate_bending_price(self, costs: Costs, multipliers: Multipliers):
        bending_cost = self.bending_count * costs.bending
        self.prices["bending"] = self.get_work_price(bending_cost, multipliers)

    def calculate_riveting_price(self, costs: Costs, multipliers: Multipliers):
        riveting_cost = self.riveting_count * costs.riveting
        self.prices["riveting"] = self.get_work_price(
            riveting_cost, multipliers
        )

    def calculate_project_price(self, costs: Costs, multipliers: Multipliers):
        project_cost = self.project_hours * costs.project
        self.prices["project"] = self.get_work_price(project_cost, multipliers)

    def calculate_cleaning_price(self, costs: Costs, multipliers: Multipliers):
        cleaning_cost = self.area * costs.cleaning
        self.prices["cleaning"] = self.get_work_price(
            cleaning_cost, multipliers
        )

    def calculate_transport_price(self, costs: Costs, multipliers: Multipliers):
        self.prices["transport"] = self.get_work_price(
            self.transport_cost, multipliers
        )

    def calculate_sundries_price(self, costs: Costs, multipliers: Multipliers):
        sundries_cost = self.sundries_count * costs.sundry
        self.prices["sundries"] = self.get_materials_price(
            sundries_cost, multipliers
        )

    @staticmethod
    def get_work_price(work_cost: float, multipliers: Multipliers) -> Price:
        return Price(
            cost=work_cost,
            final=work_cost
            * multipliers.work
            * multipliers.manager
            * multipliers.vat,
        )

    @staticmethod
    def get_materials_price(
        materials_cost: float, multipliers: Multipliers
    ) -> Price:
        return Price(
            cost=materials_cost,
            final=materials_cost
            * multipliers.materials
            * multipliers.manager
            * multipliers.vat,
        )


@dataclass
class SheetItem(BaseItem):
    sheet_cost: float = 0.0
    sheet_area: float = 0.0
    extra_welding_length: float = 0.0
    sundries_count: int = 0
    bending_count: int = 0
    riveting_count: int = 0

    def __str__(self) -> str:
        return f"{self.name}: {self.prices['total']}"

    @property
    def welding_length(self) -> float:
        return self.sundry_welding_count * 10 + self.extra_welding_length

    @property
    def area(self) -> float:
        return self.sheet_area

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
        self.prices["sheet"] = self.get_materials_price(
            self.sheet_cost, multipliers
        )
        self.calculate_welding_price(costs, multipliers)
        self.calculate_bending_price(costs, multipliers)
        self.calculate_riveting_price(costs, multipliers)
        self.calculate_weld_cleaning_price(costs, multipliers)
        self.calculate_transport_price(costs, multipliers)
        self.calculate_project_price(costs, multipliers)
        self.calculate_cleaning_price(costs, multipliers)
        self.calculate_painting_price(costs, multipliers)
        self.calculate_sundries_price(costs, multipliers)

        self.prices["total"] = Price(
            cost=sum(price.cost for price in self.prices.values()),
            final=sum(price.final for price in self.prices.values()),
        )

    def calculate_weld_cleaning_price(
        self, costs: Costs, multipliers: Multipliers
    ):
        weld_cleaning_length = 0
        if self.is_weld_cleaned:
            weld_cleaning_length = self.welding_length
        weld_cleaning_cost = weld_cleaning_length * costs.weld_cleaning
        self.prices["weld_cleaning"] = self.get_work_price(
            weld_cleaning_cost, multipliers
        )


@dataclass
class TubeItem(BaseItem):
    extra_sundries_count: int = 0
    extra_riveting_count: int = 0

    def __post_init__(self):
        super().__post_init__()
        self.tubes: list[Tube] = []
        self.sheet_items: list[SheetItem] = []

    def __getitem__(self, key: int) -> Tube:
        return self.tubes[key]

    def __str__(self) -> str:
        result = f"{self.name}: {self.prices['total']}\n"
        for tube in self.tubes:
            result += f"\t{tube}\n"
        for sheet in self.sheet_items:
            result += f"\t{sheet}\n"

        result += f"\n\tРезка: {self.prices['cutting']}\n"
        for tube in self.tubes:
            result += f"\t\t{tube}: {tube.cutting_length:,.2f} мм, {tube.cutting_cost:,.2f} руб.\n"
            if tube.left_cut is not None:
                result += f'\t\t\t{tube.left_cut.angle}°: {tube.pipe.get_cut_length(tube.left_cut):,.2f} мм\n'
            if tube.right_cut is not None:
                result += f'\t\t\t{tube.right_cut.angle}°: {tube.pipe.get_cut_length(tube.right_cut):,.2f} мм\n'
            for hole in tube.holes:
                result += f'\t\t\t{hole}: {hole.length:,.2f} мм\n'
        result += "\n"

        sorted_prices = dict(
            sorted(
                self.prices.items(), key=lambda item: item[1].cost, reverse=True
            )
        )
        del sorted_prices["total"]
        del sorted_prices["cutting"]
        for key, price in sorted_prices.items():
            result += f"\t{key}:\t\t{price}\n"
        return result

    @property
    def sundries_count(self) -> int:
        return (
            sum(sheet.sundries_count for sheet in self.sheet_items)
            + self.extra_sundries_count
        )

    @property
    def bending_count(self) -> int:
        return sum(tube.bending_count for tube in self.tubes) + sum(
            sheet.bending_count for sheet in self.sheet_items
        )

    @property
    def riveting_count(self) -> int:
        return (
            sum(sheet.riveting_count for sheet in self.sheet_items)
            + self.extra_sundries_count
        )

    @property
    def incuts_count(self) -> int:
        return sum(tube.incuts_count for tube in self.tubes)

    @property
    def cutting_length(self) -> float:
        return sum(tube.cutting_length for tube in self.tubes) + sum(
            sheet.cutting_length for sheet in self.sheet_items
        )

    @property
    def cutting_cost(self) -> float:
        return sum(tube.cutting_cost for tube in self.tubes)

    @property
    def welding_length(self) -> float:
        return (
            sum(tube.welding_length for tube in self.tubes)
            + sum(sheet.welding_length for sheet in self.sheet_items)
            + self.sundry_welding_count * 10
        )

    @property
    def area(self) -> float:
        result = sum(tube.area for tube in self.tubes)
        return result

    def calculate_price(
        self,
        adjusted_cutting_cost: float,
        costs: Costs,
        multipliers: Multipliers,
    ) -> None:
        for sheet in self.sheet_items:
            sheet.calculate_price(0.0, costs, multipliers)

        self.prices["cutting"] = self.get_work_price(
            adjusted_cutting_cost, multipliers
        )
        self.calculate_pipe_price(costs, multipliers)
        self.calculate_sheet_price(costs, multipliers)
        self.calculate_welding_price(costs, multipliers)
        self.calculate_bending_price(costs, multipliers)
        self.calculate_riveting_price(costs, multipliers)
        self.calculate_weld_cleaning_price(costs, multipliers)
        self.calculate_transport_price(costs, multipliers)
        self.calculate_project_price(costs, multipliers)
        self.calculate_cleaning_price(costs, multipliers)
        self.calculate_painting_price(costs, multipliers)
        self.calculate_sundries_price(costs, multipliers)

        self.prices["total"] = Price(
            cost=sum(price.cost for price in self.prices.values()),
            final=sum(price.final for price in self.prices.values()),
        )

    def calculate_pipe_price(self, costs: Costs, multipliers: Multipliers):
        pipe_cost = sum(tube.pipe_cost for tube in self.tubes)
        self.prices["pipe"] = self.get_materials_price(pipe_cost, multipliers)

    def calculate_sheet_price(self, costs: Costs, multipliers: Multipliers):
        sheet_cost = sum(sheet.sheet_cost for sheet in self.sheet_items)
        self.prices["sheet"] = self.get_materials_price(sheet_cost, multipliers)

    def calculate_weld_cleaning_price(
        self, costs: Costs, multipliers: Multipliers
    ):
        weld_cleaning_length = sum(
            tube.length for tube in self.tubes if tube.is_weld_cleaned
        )
        if self.is_weld_cleaned:
            weld_cleaning_length += self.welding_length
        weld_cleaning_cost = weld_cleaning_length * costs.weld_cleaning
        self.prices["weld_cleaning"] = self.get_work_price(
            weld_cleaning_cost, multipliers
        )

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
