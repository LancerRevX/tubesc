"""tubesc example"""

from calculator import (
    Order,
    RectPipe,
    Costs,
    Multipliers,
    Cut,
    RectHole,
    RoundHole,
    TubeItem,
    Tube,
    SheetItem,
)


pipe = RectPipe(
    width=100,
    height=100,
    thickness=4,
    cost=1018 / 1000,
    incut_cost=5,
    cutting_cost=34 / 1000,
    carrying_cost=75 / 1000,
)
costs = Costs(
    welding=600 / 1000,
    sundry=5,
    cleaning=1000 / 1_000_000,
    weld_cleaning=90 / 1000,
    painting=260 / 1_000_000,
    paint=280 / 1_000_000,
    riveting=10,
    bending=15,
    project=500,
)
multipliers = Multipliers(work=2.0, materials=1.3, manager=1.1, vat=1.2)

order = Order(
    1,
    "Мой заказ",
    items=[
        TubeItem(
            "Труба 4500",
            count=13,
            project_hours=1,
            is_painted=True,
            transport_cost=450,
            is_weld_cleaned=True,
            tubes=[
                Tube(
                    pipe,
                    4500,
                    is_weld_cleaned=True,
                    is_cleaned=True,
                    left_cut=Cut(45, welding_ratio=0.5),
                    right_cut=Cut(90, welding_ratio=1),
                    holes=[RectHole(98, 398), RoundHole(8, count=4)],
                ),
                Tube(
                    pipe,
                    647,
                    is_weld_cleaned=True,
                    is_cleaned=True,
                    left_cut=Cut(45, welding_ratio=0.5),
                    right_cut=Cut(90, welding_ratio=1),
                    holes=[RectHole(98, 398), RoundHole(8, count=4)],
                ),
            ],
            sheet_items=[
                SheetItem("Фланец", 300),
                SheetItem("Заглушка", 150),
                SheetItem(
                    "Кронштейн БП",
                    75,
                    bending_count=2,
                    sundries_count=4,
                    riveting_count=4,
                ),
            ],
        ),
    ],
)

order.calculate(costs, multipliers)

for item in order:
    print(item)
