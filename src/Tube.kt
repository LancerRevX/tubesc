class Tube(val item: TubeItem, val pipe: Pipe, val costs: Costs, val length: Double) {
    val holes = mutableListOf<Hole>()

    fun addRoundHole(
        diameter: Double,
        count: Int = 1,
        through: Boolean = false
    ) {
        val hole = RoundHole(this, diameter, count, through)
        holes.add(hole)
    }
}