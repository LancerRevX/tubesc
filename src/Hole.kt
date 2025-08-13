import kotlin.math.PI

abstract class Hole(
    val tube: Tube, val count: Int = 1, val through: Boolean = false
) {
    abstract fun length(): Double

    abstract fun sizeString(): String

    override fun toString(): String {
        var result = "Отв. "
        if (through) {
            result += "скв. "
        }
        result += sizeString()
        if (count > 1) {
            result += " - $count шт"
        }
        return result
    }

    fun count(): Int {
        return count * (if (through) 2 else 1)
    }

    fun cuttingCost(): Double {
        val oneHoleCost =
            tube.pipe.costs.incut + tube.pipe.costs.cutting * length()
        return oneHoleCost * count()
    }
}

class RoundHole(
    tube: Tube, val diameter: Double, count: Int = 1, through: Boolean = false
) : Hole(tube, count, through) {
    override fun length(): Double {
        return diameter * PI * count * (if (through) 2 else 1)
    }

    override fun sizeString(): String {
        return "ф$diameter"
    }
}