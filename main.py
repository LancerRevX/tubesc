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

order = Order(1040, "Проф-система")

with order.add_tube_item("Труба 4500") as item:
    item.count = 13
    item.is_painted = True
    item.project_hours = 1
    item.transport_cost = 450
    item.is_weld_cleaned = True
    with item.add_tube(pipe, 4500) as tube:
        tube.is_weld_cleaned = True
        tube.is_cleaned = True
        tube.left_cut = Cut(45, welding_ratio=0.5)
        tube.right_cut = Cut(90, welding_ratio=1)
        tube.add_hole(RectHole(98, 398))
        tube.add_hole(RoundHole(8, count=4))
    with item.add_tube(pipe, 647) as tube:
        tube.is_weld_cleaned = True
        tube.is_cleaned = True
        tube.left_cut = Cut(45, welding_ratio=0.5)
        tube.right_cut = Cut(90, welding_ratio=1)
        tube.add_hole(RectHole(98, 398))
        tube.add_hole(RoundHole(8, count=4))
    with item.add_sheet_item("Фланец") as sheet:
        sheet.sheet_cost = 300
    with item.add_sheet_item("Заглушка") as sheet:
        sheet.sheet_cost = 100
    with item.add_sheet_item("Кронштейн БП") as sheet:
        sheet.sheet_cost = 34
        sheet.bending_count = 2
        sheet.sundries_count = 4
        sheet.riveting_count = 4

with order.add_sheet_item("Лючок") as item:
    item.sheet_cost = 332
    item.sheet_area = 98 * 398 * 2
    item.is_painted = True

with order.add_sheet_item("Кронштейн БП") as item:
    item.sheet_cost = 153
    item.sheet_area = 75 * 150 * 2
    item.sundries_count = 4
    item.riveting_count = 4
    item.is_painted = True

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
