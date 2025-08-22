from dataclasses import dataclass, field, KW_ONLY
from contextlib import contextmanager
from abc import ABC, abstractmethod

from . import Tube, Costs, Multipliers, Pipe, Price


@dataclass
class BaseItem(ABC):
    name: str
    _: KW_ONLY
    count: int = 1
    project_hours: float = 0
    sundry_welding_count: int = 0
    is_painted: bool = False
    is_cleaned: bool = False
    transport_cost: float = 0.0
    is_weld_cleaned: bool = False
    drying_divider: int = 1

    def __post_init__(self) -> None:
        self.prices: dict[str, Price] = dict()
        self.calculation_steps = [
            self.calculate_bending_price,
        ]

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

    @property
    @abstractmethod
    def countersink_count(self) -> int:
        pass

    @property
    @abstractmethod
    def threading_count(self) -> int:
        pass

    @abstractmethod
    def calculate_price(
        self,
        adjusted_cutting_cost: float,
        costs: Costs,
        multipliers: Multipliers,
    ):
        pass

    def calculate_drying_price(self, costs: Costs, multipliers: Multipliers):
        if not self.is_painted:
            self.prices["drying"] = Price()
            return
        
        drying_cost = costs.drying / self.drying_divider
        self.prices["drying"] = self.get_work_price(drying_cost, multipliers)

    def calculate_painting_price(self, costs: Costs, multipliers: Multipliers):
        if not self.is_painted:
            self.prices["painting"] = Price()
            return

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

    def calculate_countersink_price(
        self, costs: Costs, multipliers: Multipliers
    ):
        countersink_cost = self.countersink_count * costs.countersink
        self.prices["countersink"] = self.get_work_price(
            countersink_cost, multipliers
        )

    def calculate_threading_price(self, costs: Costs, multipliers: Multipliers):
        threading_cost = self.threading_count * costs.threading
        self.prices["threading"] = self.get_work_price(
            threading_cost, multipliers
        )

    def calculate_project_price(self, costs: Costs, multipliers: Multipliers):
        project_cost = self.project_hours * costs.project / self.count
        self.prices["project"] = self.get_work_price(project_cost, multipliers)

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
    sheet_cost: float
    sheet_area: float | None = None
    extra_welding_length: float = 0.0
    sundries_count: int = 0  # pyright: ignore[reportIncompatibleMethodOverride]
    bending_count: int = 0  # pyright: ignore[reportIncompatibleMethodOverride]
    riveting_count: int = 0  # pyright: ignore[reportIncompatibleMethodOverride]
    countersink_count: int = 0 # pyright: ignore[reportIncompatibleMethodOverride]
    threading_count: int = 0 # pyright: ignore[reportIncompatibleMethodOverride]

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.is_painted and self.sheet_area is None:
            raise ValueError('is_painted requires sheet_area to be set')

    def __str__(self) -> str:
        result = f"{self.name}: {self.prices['total']}\n"

        if self.prices["sheet"].cost > 0:
            result += f"\tЛистовой металл: {self.prices['sheet']}\n\n"

        if self.prices["sundries"].cost > 0:
            result += f"\tМетизы: {self.sundries_count} шт, {self.prices['sundries']}\n\n"

        if self.prices["riveting"].cost > 0:
            result += f"\tЗаклёпывание: {self.riveting_count} шт, {self.prices['riveting']}\n\n"

        if self.prices["bending"].cost > 0:
            result += f"\tГибка: {self.bending_count} шт, {self.prices['bending']}\n\n"

        if self.prices["welding"].cost > 0:
            result += f"\tСварка: {self.welding_length:,.2f} мм, {self.prices['welding']}\n\n"

        if self.prices["countersink"].cost > 0:
            result += f"\tЗенковка: {self.countersink_count} шт, {self.prices['countersink']}\n"

        # if self.prices["cleaning"].cost > 0:
        #     result += f"\tЗачистка корщёткой: {self.area:,.2f} мм2, {self.prices['cleaning']}\n\n"

        if self.prices["painting"].cost > 0:
            result += f"\tПокраска: {self.area / 1_000_000:,.2f} м2, {self.prices['painting']}\n\n"

        if self.prices["project"].cost > 0:
            result += f"\tПроектировка: {self.project_hours} ч / {self.count} шт, {self.prices['project']}\n\n"

        return result

    @property
    def welding_length(self) -> float:
        return self.sundry_welding_count * 10 + self.extra_welding_length

    @property
    def area(self) -> float:
        return self.sheet_area # type: ignore

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
        self.calculate_countersink_price(costs, multipliers)
        self.calculate_threading_price(costs, multipliers)

        self.prices["total"] = Price(
            cost=sum(price.cost for price in self.prices.values()),
            final=sum(price.final for price in self.prices.values()),
        )

    def calculate_cleaning_price(self, costs: Costs, multipliers: Multipliers):
        if not self.is_cleaned:
            self.prices["cleaning"] = Price()
            return
        cleaning_cost = self.area * costs.cleaning
        self.prices["cleaning"] = self.get_work_price(
            cleaning_cost, multipliers
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
    extra_bending_count: int = 0
    tubes: list[Tube] = field(default_factory=list[Tube])
    sheet_items: list[SheetItem] = field(default_factory=list[SheetItem])

    def __post_init__(self):
        super().__post_init__()
        # self.tubes: list[Tube] = []
        # self.sheet_items: list[SheetItem] = []

    def __getitem__(self, key: int) -> Tube:
        return self.tubes[key]

    def __str__(self) -> str:
        result = f"{self.name} - {self.count} шт: {self.prices['total']} * {self.count} = {self.prices['total'].cost * self.count:,.2f} руб -> {self.prices['total'].final * self.count:,.2f} руб\n"
        for tube in self.tubes:
            result += f"\t{tube}\n"
        for sheet in self.sheet_items:
            result += f"\t{sheet.name}: {sheet.prices['total']}\n"
        result += "\n"

        if self.prices["pipe"].cost > 0:
            result += f"\tТруба: {self.prices['pipe']}\n"
            for tube in self.tubes:
                if tube.pipe_cost == 0:
                    continue
                result += f"\t\t{tube}: {tube.pipe.cost * 1000:,.2f} руб/м, {tube.pipe_cost:,.2f} руб\n"
            result += "\n"

        result += f"\tРезка: {self.prices['cutting']} \n"
        for tube in self.tubes:
            result += f"\t\t{tube}: {tube.incuts_count} врезки / {tube.cutting_length:,.2f} мм, {tube.cutting_cost:,.2f} руб\n"
            if tube.left_cut is not None:
                result += f"\t\t\t{tube.left_cut}: {tube.pipe.get_cut_length(tube.left_cut):,.2f} мм\n"
            if tube.right_cut is not None:
                result += f"\t\t\t{tube.right_cut}: {tube.pipe.get_cut_length(tube.right_cut):,.2f} мм\n"
            for hole in tube.holes:
                result += f"\t\t\t{hole}: {hole.length:,.2f} мм\n"
        result += "\n"

        if self.prices["welding"].cost > 0:
            result += f"\tСварка: {self.welding_length:,.2f} мм, {self.prices['welding']}\n"
            for tube in self.tubes:
                if tube.welding_length == 0:
                    continue
                result += f"\t\t{tube}: {tube.welding_length:,.2f} мм"
                if tube.count > 1:
                    total_welding_length = tube.welding_length * tube.count
                    result += f" * {tube.count} = {total_welding_length:,.2f} мм"
                result += '\n'
            for sheet in self.sheet_items:
                if sheet.welding_length == 0:
                    continue
                result += f"\t\t{sheet.name} - {sheet.count} шт: {sheet.welding_length:,.2f} мм * {sheet.count} = {sheet.welding_length * sheet.count:,.2f} мм\n"
            if self.sundry_welding_count > 0:
                result += f"\t\tТочки - {self.sundry_welding_count} шт: 10 * {self.sundry_welding_count} = {self.sundry_welding_count * 10} мм\n"
            result += "\n"

        if self.prices["weld_cleaning"].cost > 0:
            result += (
                f"\tЗачистка сварного шва: {self.prices['weld_cleaning']}\n"
            )
            for tube in self.tubes:
                if not tube.is_weld_cleaned:
                    continue
                result += f"\t\t{tube}: {tube.length} мм\n"
            if self.is_weld_cleaned:
                result += f"\t\tСварка: {self.welding_length:,.2f} мм\n"
            result += "\n"

        if self.prices["cleaning"].cost > 0:
            result += f"\tЗачистка корщёткой: {self.prices['cleaning']}\n"
            for tube in self.tubes:
                if not tube.is_cleaned:
                    continue
                result += f"\t\t{tube}: {tube.area / 1_000_000:,.2f} м2\n"
            for sheet in self.sheet_items:
                if not sheet.is_cleaned:
                    continue
                result += (
                    f"\t\t{sheet.name}: {sheet.area / 1_000_000:,.2f} м2\n"
                )
            result += "\n"

        if self.prices["painting"].cost > 0:
            result += f"\tПокраска: {self.area / 1_000_000:,.2f} м2, {self.prices['painting']}\n\n"

        if self.prices['drying'].cost > 0:
            result += f"\tСушка: {self.prices['drying']}\n\n"

        if self.prices["sundries"].cost > 0:
            result += f"\tМетизы: {self.sundries_count} шт, {self.prices['sundries']}\n"
            for sheet in self.sheet_items:
                if sheet.sundries_count == 0:
                    continue
                result += f"\t\t{sheet.name}: {sheet.sundries_count} шт\n"
            result += "\n"

        if self.prices["riveting"].cost > 0:
            result += f"\tЗаклёпывание: {self.riveting_count} шт, {self.prices['riveting']}\n"
            for sheet in self.sheet_items:
                if sheet.riveting_count == 0:
                    continue
                result += f"\t\t{sheet.name}: {sheet.riveting_count} шт\n"
            result += "\n"

        if self.prices["countersink"].cost > 0:
            result += f"\tЗенковка: {self.countersink_count} шт, {self.prices['countersink']}\n"
            for sheet in self.sheet_items:
                if sheet.countersink_count == 0:
                    continue
                result += f"\t\t{sheet.name}: {sheet.countersink_count} шт\n"
            result += "\n"

        if self.prices["threading"].cost > 0:
            result += f"\tНарезка резьбы: {self.threading_count} шт, {self.prices['threading']}\n"
            for sheet in self.sheet_items:
                if sheet.threading_count == 0:
                    continue
                result += f"\t\t{sheet.name}: {sheet.threading_count} шт\n"
            for tube in self.tubes:
                if tube.threading_count == 0:
                    continue
                result += f"\t\t{tube}: {tube.threading_count} шт\n"
            result += "\n"

        if self.prices["bending"].cost > 0:
            result += (
                f"\tГибка: {self.bending_count} шт, {self.prices['bending']}\n"
            )
            for tube in self.tubes:
                if tube.bending_count == 0:
                    continue
                result += f"\t\t{tube}: {tube.bending_count} шт\n"
            for sheet in self.sheet_items:
                if sheet.bending_count == 0:
                    continue
                result += f"\t\t{sheet.name}: {sheet.bending_count} шт\n"
            result += "\n"

        result += f"\tТаскание: {self.prices['carrying']}\n\n"

        if self.prices["sheet"].cost > 0:
            result += f"\tЛистовой металл: {self.prices['sheet']}\n"
            for sheet in self.sheet_items:
                result += f"\t\t{sheet.name}"
                if sheet.count > 1:
                    result += f" - {sheet.count} шт"
                result += f": {sheet.sheet_cost:,.2f} руб\n"
            result += "\n"

        if self.prices["transport"].cost > 0:
            result += f"\tТранспортировка: {self.prices['transport']}\n\n"

        result += f"\tПроектировка: {self.project_hours} ч / {self.count} шт, {self.prices['project']}\n\n"

        return result

    @property
    def sundries_count(self) -> int:
        return (
            sum(sheet.sundries_count * sheet.count for sheet in self.sheet_items)
            + sum(tube.sundries_count * tube.count for tube in self.tubes)
            + self.extra_sundries_count
        )

    @property
    def countersink_count(self) -> int:
        return sum(sheet.countersink_count * sheet.count for sheet in self.sheet_items) + sum(tube.countersink_count * tube.count for tube in self.tubes)

    @property
    def threading_count(self) -> int:
        return sum(
            sheet.threading_count * sheet.count for sheet in self.sheet_items
        ) + sum(tube.threading_count * tube.count for tube in self.tubes)

    @property
    def bending_count(self) -> int:
        return sum(tube.bending_count * tube.count for tube in self.tubes) + sum(
            sheet.bending_count for sheet in self.sheet_items
        ) + self.extra_bending_count

    @property
    def riveting_count(self) -> int:
        return (
            sum(sheet.riveting_count * sheet.count for sheet in self.sheet_items)
            + sum(tube.riveting_count * tube.count for tube in self.tubes)
            + self.extra_sundries_count
        )

    @property
    def incuts_count(self) -> int:
        return sum(tube.incuts_count * tube.count for tube in self.tubes)

    @property
    def cutting_length(self) -> float:
        return sum(tube.cutting_length * tube.count for tube in self.tubes) + sum(
            sheet.cutting_length for sheet in self.sheet_items
        )

    @property
    def cutting_cost(self) -> float:
        return sum(tube.cutting_cost * tube.count for tube in self.tubes)

    @property
    def welding_length(self) -> float:
        return (
            sum(tube.welding_length * tube.count for tube in self.tubes)
            + sum(
                sheet.welding_length * sheet.count for sheet in self.sheet_items
            )
            + self.sundry_welding_count * 10
        )

    @property
    def area(self) -> float:
        result = sum(tube.area * tube.count for tube in self.tubes)
        return result

    def calculate_price(
        self,
        adjusted_cutting_cost: float,
        costs: Costs,
        multipliers: Multipliers,
    ) -> None:
        for sheet in self.sheet_items:
            sheet.calculate_price(0.0, costs, multipliers)

        cutting_cost = self.cutting_cost
        if cutting_cost < 500:
            cutting_cost = 500
        self.prices["cutting"] = self.get_work_price(
            cutting_cost, multipliers
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
        self.calculate_carrying_price(multipliers)
        self.calculate_countersink_price(costs, multipliers)
        self.calculate_threading_price(costs, multipliers)
        self.calculate_drying_price(costs, multipliers)

        self.prices["total"] = Price(
            cost=sum(price.cost for price in self.prices.values()),
            final=sum(price.final for price in self.prices.values()),
        )

    def calculate_pipe_price(self, costs: Costs, multipliers: Multipliers):
        pipe_cost = sum(tube.pipe_cost * tube.count for tube in self.tubes)
        self.prices["pipe"] = self.get_materials_price(pipe_cost, multipliers)

    def calculate_cleaning_price(self, costs: Costs, multipliers: Multipliers):
        cleaning_cost = sum(
            tube.area * costs.cleaning for tube in self.tubes if tube.is_cleaned
        )
        self.prices["cleaning"] = self.get_work_price(
            cleaning_cost, multipliers
        )

    def calculate_sheet_price(self, costs: Costs, multipliers: Multipliers):
        sheet_cost = sum(
            sheet.sheet_cost * sheet.count for sheet in self.sheet_items
        )
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

    def calculate_carrying_price(self, multipliers: Multipliers):
        carrying_cost = sum(tube.carrying_cost * tube.count for tube in self.tubes)
        self.prices["carrying"] = self.get_work_price(
            carrying_cost, multipliers
        )

    @contextmanager
    def add_tube(self, pipe: Pipe, length: float):
        tube = Tube(pipe, length)
        self.tubes.append(tube)
        yield tube

    @contextmanager
    def add_sheet_item(self, name: str):
        item = SheetItem(name, 0)
        self.sheet_items.append(item)
        yield item
