import kotlin.math.PI

data class PipeCosts(
    val pipe: Double,
    val incut: Double,
    val cutting: Double,
    val carrying: Double
) {}

abstract class Pipe(val thickness: Double, val costs: PipeCosts) {
    abstract fun perimeter(): Double
}

class RoundPipe(val diameter: Double, thickness: Double, costs: PipeCosts) :
    Pipe(thickness, costs) {
    override fun perimeter(): Double {
        return diameter * PI
    }
}

class RectPipe(
    val width: Double, val height: Double, thickness: Double, costs: PipeCosts
) : Pipe(thickness, costs) {
    override fun perimeter(): Double {
        return (width + height) * 2
    }

}




