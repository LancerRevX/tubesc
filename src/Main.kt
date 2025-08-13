fun main() {
    val costs = Costs(
        welding = 1.0,
        sundry = 5.0,
        cleaning = 90.0 / 1000,
        weldCleaning = 1000.0
    )

    val pipe = RoundPipe(
        30.0, 3.5, PipeCosts(
            pipe = 30.0, incut = 5.0, cutting = 34.0, carrying = 75.0
        )
    )

    val order = Order(1, "Мой заказ", costs).apply {
        addTubeItem("Труба").apply {
            isPainted = true
        }
    }
}