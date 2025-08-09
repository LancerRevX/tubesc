from dataclasses import dataclass

@dataclass
class Price:
    cost: float
    final: float

    def __str__(self) -> str:
        return f'{self.cost:,.2f} руб -> {self.final:,.2f} руб'