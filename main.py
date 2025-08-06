from calculator import (
    Order,
    RectPipe,
    Prices,
    Multipliers,
    Item,
    Cut,
    RectHole,
    RoundHole,
)

pipe = RectPipe(
    width=100, height=100, price=1018 / 1000, incut_price=5, cutting_price=34
)
prices = Prices(
    welding=600 / 1000,
    sundry=5,
    cleaning=1000 / 1_000_000,
    weld_cleaning=90 / 1000,
    painting=560,
    riveting=10,
    bending=15,
)
multipliers = Multipliers(work=2.0, materials=1.3)

order = Order(prices, multipliers, 1040, "Проф-система")

with order.add_item("Труба 4500") as item:
    item.is_painted = True
    with item.add_tube(pipe, 4500) as tube:
        tube.left_cut = Cut(45)
        tube.add_holes(RectHole(98, 398))
        tube.add_holes(RoundHole(8), 4)
    with item.add_item("Фланец") as item:
        item.base_price = 300
        item.welding_length = 100 * 4
        item.is_cleaned = True
        item.is_painted = True
