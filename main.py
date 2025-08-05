from calculator import Order, Pipe, Cut

pipe = Pipe(100, 100, 1018/1000)

order = Order('1040', 'Проф-система')

item1 = order.add_item('Труба 4500')
tube1 = item1.add_tube(pipe, 4500)
tube1.is_cleaned = True
tube1.left_cut = Cut(90)
tube1.add_hole(Hole(90, 348))
