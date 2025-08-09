from calculator import (
    Order,
    RectPipe,
    Costs,
    Multipliers,
    Cut,
    RectHole,
    RoundHole,
    # TubeItem,
    # Tube,
    # SheetItem,
)

pipe = RectPipe(
    width=100,
    height=100,
    thickness=4,
    cost=1018 / 1000,
    incut_cost=5,
    cutting_cost=34 / 1000,
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

order = Order(costs, multipliers, 1040, "Проф-система")

with order.add_tube_item("Труба 4500") as item:
    item.is_painted = True
    item.project_hours = 1
    item.transport_cost = 450
    with item.add_tube(pipe, 4500) as tube:
        tube.is_weld_cleaned = True
        tube.is_cleaned = True
        tube.left_cut = Cut(45, welding_ratio=0.5)
        tube.right_cut = Cut(90, welding_ratio=1)
        tube.add_holes(RectHole(98, 398))
        tube.add_holes(RoundHole(8), 4)
    with item.add_tube(pipe, 647) as tube:
        tube.is_weld_cleaned = True
        tube.is_cleaned = True
        tube.left_cut = Cut(45, welding_ratio=0.5)
        tube.right_cut = Cut(90, welding_ratio=1)
        tube.add_holes(RectHole(98, 398))
        tube.add_holes(RoundHole(8), 4)
    with item.add_sheet_item("Фланец") as sheet:
        sheet.sheet_cost = 300
    with item.add_sheet_item("Заглушка") as sheet:
        sheet.sheet_cost = 100
    with item.add_sheet_item("Кронштейн БП") as sheet:
        sheet.sheet_cost = 34
        sheet.bending_count = 2
        sheet.sundries_count = 4
        sheet.riveting_count = 4

order.calculate_price()

for item in order:
    print(item)
