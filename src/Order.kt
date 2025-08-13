class Order(val number: Int, val name: String, val costs: Costs) {
    val items = mutableListOf<Item>()

    fun addTubeItem(name: String): TubeItem {
        val item = TubeItem(this, name, costs)
        items.add(item)
        return item
    }
}
