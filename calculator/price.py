from dataclasses import dataclass

@dataclass
class Price:
    cost: float = 0.0
    final: float = 0.0

    def __str__(self) -> str:
        return f'{self.cost:,.2f} руб -> {self.final:,.2f} руб'