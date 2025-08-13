abstract class Item(val order: Order, val name: String, val costs: Costs) {
    var isPainted = false
}

class TubeItem(order: Order, name: String, costs: Costs) : Item(order, name, costs) {
    val tubes = mutableListOf<Tube>()

    fun addTube(pipe: Pipe, length: Double): Tube {
        val tube = Tube(this, pipe, costs, length)
        tubes.add(tube)
        return tube
    }
}